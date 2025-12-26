async function getJson(url) {
  const r = await fetch(url, {credentials: 'include'});
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || data.error || 'Request failed');
  return data;
}

async function patchJson(url, body) {
  const r = await fetch(url, {
    method: 'PATCH',
    headers: {'Content-Type': 'application/json'},
    credentials: 'include',
    body: JSON.stringify(body),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || data.error || 'Request failed');
  return data;
}

function setText(id, t) {
  const el = document.getElementById(id);
  if (el) el.textContent = t ?? '';
}

function setHTML(id, h) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = h ?? '';
}

async function logout() {
  await fetch('/auth/logout', {method: 'POST', credentials: 'include'});
  window.location.href = '/';
}

let current = null;
let allClients = [];

function renderList(list) {
  return list
    .map((c) => {
      const title = `#${c.user_id}  age=${c.age_group ?? '-'}  occ=${c.occupation_type ?? '-'}`;
      return `<div class="movie" data-id="${c.user_id}"><div><strong>${title}</strong></div><div class="muted">income=${c.amt_income_total ?? '-'} manager_id=${c.manager_id ?? '-'}</div></div>`;
    })
    .join('') || '<div class="muted">Empty</div>';
}

function renderForm(c) {
  const fields = [
    'manager_id',
    'code_gender','flag_own_car','flag_own_realty',
    'cnt_children','amt_income_total',
    'name_income_type','name_education_type','name_family_status','name_housing_type',
    'days_birth','days_employed',
    'flag_work_phone','flag_phone','flag_email',
    'occupation_type','cnt_fam_members','age_group','days_employed_bin'
  ];
  return fields.map((f) => {
    const v = c[f] ?? '';
    return `<div class="stack"><label class="muted">${f}</label><input class="input" id="f_${f}" value="${String(v)}" /></div>`;
  }).join('');
}

function collectForm() {
  const out = {};
  const ids = document.querySelectorAll('[id^="f_"]');
  ids.forEach((el) => {
    const key = el.id.slice(2);
    const raw = el.value;
    if (raw === '') return;
    if (['cnt_children','days_birth','days_employed','flag_work_phone','flag_phone','flag_email','cnt_fam_members','manager_id'].includes(key)) {
      out[key] = Number(raw);
      if (Number.isNaN(out[key])) delete out[key];
    } else if (key === 'amt_income_total') {
      out[key] = Number(raw);
      if (Number.isNaN(out[key])) delete out[key];
    } else {
      out[key] = raw;
    }
  });
  return out;
}

async function load() {
  const me = await getJson('/auth/me');
  setText('who', `user_id=${me.user_id} role=${me.role}`);
  const all = document.getElementById('all_toggle').checked;
  const clients = await getJson(`/api/manager/clients?all=${all ? 'true' : 'false'}`);
  allClients = clients;
  setHTML('clients_list', renderList(clients));
  bindList();
}

function bindList() {
  document.querySelectorAll('#clients_list .movie').forEach((el) => {
    el.onclick = () => {
      const id = Number(el.getAttribute('data-id'));
      current = allClients.find((x) => x.user_id === id);
      if (!current) return;
      setText('sel', `Selected client_id=${id}`);
      setHTML('form', renderForm(current));
      document.getElementById('btn_save').disabled = false;
      setText('save_msg', '');
    };
  });
}

function applySearch() {
  const q = document.getElementById('q').value.trim().toLowerCase();
  const filtered = allClients.filter((c) => {
    if (!q) return true;
    return JSON.stringify(c).toLowerCase().includes(q);
  });
  setHTML('clients_list', renderList(filtered));
  bindList();
}

async function main() {
  try {
    await load();
  } catch (e) {
    window.location.href = '/';
    return;
  }

  document.getElementById('btn_logout').onclick = logout;
  document.getElementById('btn_reload').onclick = load;
  document.getElementById('all_toggle').onchange = load;
  document.getElementById('q').oninput = applySearch;

  document.getElementById('btn_save').onclick = async () => {
    if (!current) return;
    setText('save_msg', '');
    try {
      const patch = collectForm();
      const upd = await patchJson(`/api/manager/clients/${current.user_id}`, patch);
      setText('save_msg', 'Saved');
      // refresh current and list
      current = upd;
      await load();
    } catch (e) {
      setText('save_msg', e.message);
    }
  };
}

main();


