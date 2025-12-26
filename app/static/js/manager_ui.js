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
let currentDetail = null;
let currentScore = null;
let editMode = false;

function renderList(list) {
  return list
    .map((c) => {
      const fio = `${c.last_name ?? ''} ${c.first_name ?? ''}`.trim();
      return `<div class="movie" data-id="${c.user_id}"><div><strong>ID:${c.user_id} ${fio || '-'}</strong></div></div>`;
    })
    .join('') || '<div class="muted">Empty</div>';
}

const FIELD_META = [
  {section: 'Личные данные'},
  {key: 'code_gender', label: 'Пол'},
  {key: 'days_birth', label: 'Дней прожито'},
  {key: 'age_group', label: 'Возрастная группа'},
  {key: 'cnt_fam_members', label: 'Количество членов семьи'},
  {key: 'name_family_status', label: 'Семейное положение'},
  {key: 'cnt_children', label: 'Количество детей'},
  {key: 'flag_own_car', label: 'Личный автомобиль'},
  {key: 'flag_own_realty', label: 'Недвижимость'},
  {key: 'flag_phone', label: 'Есть личный телефон'},
  {key: 'flag_email', label: 'Есть email'},

  {section: 'Профессиональные данные'},
  {key: 'name_education_type', label: 'Образование'},
  {key: 'name_housing_type', label: 'Образ жизни'},
  {key: 'occupation_type', label: 'Род деятельности'},
  {key: 'days_employed', label: 'Трудовой стаж'},
  {key: 'days_employed_bin', label: 'Группа по стажу'},
  {key: 'amt_income_total', label: 'Годовой доход'},
  {key: 'name_income_type', label: 'Источник дохода'},
  {key: 'flag_work_phone', label: 'Есть рабочий телефон'},
];

const AGE_GROUP_OPTIONS = ["18-25","25-35","35-45","45-55","55-65","65+"];
const DAYS_EMPLOYED_BIN_OPTIONS = ["<1 year","1-3 year","3-5 year","5-10 year","10-40 year","40+ year"];

function _select(id, value, options, disabled) {
  const opts = ['<option value=""></option>']
    .concat(options.map(o => `<option value="${o}" ${String(o)===String(value) ? 'selected' : ''}>${o}</option>`))
    .join('');
  return `<select class="input" id="${id}" ${disabled ? 'disabled' : ''}>${opts}</select>`;
}

function renderForm(client, disabled) {
  if (!client) return '';
  const chunks = [];
  chunks.push('<div class="form-grid">');
  for (const item of FIELD_META) {
    if (item.section) {
      chunks.push(`<div class="section-title">${item.section}</div>`);
      continue;
    }
    const f = item.key;
    const v = client[f] ?? '';
    let control = '';
    if (f === 'age_group') {
      control = _select(`f_${f}`, v, AGE_GROUP_OPTIONS, disabled);
    } else if (f === 'days_employed_bin') {
      control = _select(`f_${f}`, v, DAYS_EMPLOYED_BIN_OPTIONS, disabled);
    } else {
      control = `<input class="input" id="f_${f}" value="${String(v)}" ${disabled ? 'disabled' : ''} />`;
    }
    chunks.push(`<div class="stack">
      <label class="muted">${item.label}</label>
      ${control}
    </div>`);
  }
  chunks.push('</div>');
  return chunks.join('');
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
  const clients = await getJson(`/api/manager/clients/summary?all=${all ? 'true' : 'false'}`);
  allClients = clients;
  setHTML('clients_list', renderList(clients));
  bindList();
}

function bindList() {
  document.querySelectorAll('#clients_list .movie').forEach((el) => {
    el.onclick = async () => {
      const id = Number(el.getAttribute('data-id'));
      current = allClients.find((x) => x.user_id === id);
      if (!current) return;
      setText('sel', `Selected client_id=${id}`);
      setText('save_msg', '');
      // load full details for edit form
      const detail = await getJson(`/api/manager/clients/${id}`);
      currentDetail = detail;
      editMode = false;
      const fio = `${detail.user.last_name} ${detail.user.first_name}`.trim();
      setText('sel', `Client #${id} — ${fio}`);
      setHTML('form', renderForm(detail.client, true));
      document.getElementById('btn_edit').disabled = false;
      document.getElementById('btn_save').disabled = true;
      document.getElementById('btn_rescore').disabled = false;
      setScoreDisplay(null);
      await loadScore(id);
    };
  });
}

function applySearch() {
  const q = document.getElementById('q').value.trim().toLowerCase();
  const filtered = allClients.filter((c) => {
    if (!q) return true;
    const fio = `${c.last_name ?? ''} ${c.first_name ?? ''}`.toLowerCase();
    return String(c.user_id).includes(q) || fio.includes(q);
  });
  setHTML('clients_list', renderList(filtered));
  bindList();
}

function scoreColor(v) {
  const clamped = Math.max(0, Math.min(1, v));
  const hue = clamped * 120; // 0 red -> 120 green
  return `hsl(${hue}, 70%, 35%)`;
}

function setScoreDisplay(probaOrNull) {
  const el = document.getElementById('score_value');
  if (!el) return;
  if (probaOrNull === null || probaOrNull === undefined) {
    el.textContent = '-';
    el.style.color = '';
    return;
  }
  const proba = Number(probaOrNull);
  // round(1 - proba, 2) like in Python
  const v = Number.isFinite(proba) ? Math.round((1 - proba) * 100) / 100 : NaN;
  const shown = Number.isFinite(v) ? v.toFixed(2) : '-';
  el.textContent = shown;
  if (Number.isFinite(v)) el.style.color = scoreColor(v);
}

async function postJson(url, body) {
  const r = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    credentials: 'include',
    body: JSON.stringify(body || {}),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || data.error || 'Request failed');
  return data;
}

async function loadScore(clientId) {
  try {
    const s = await getJson(`/api/manager/clients/${clientId}/score`);
    currentScore = s;
    if (!s) setScoreDisplay(null);
    else setScoreDisplay(s.score);
  } catch (_) {
    setScoreDisplay(null);
  }
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

  document.getElementById('btn_edit').onclick = async () => {
    if (!currentDetail) return;
    editMode = true;
    setText('save_msg', '');
    setHTML('form', renderForm(currentDetail.client, false));
    document.getElementById('btn_save').disabled = false;
  };
  document.getElementById('btn_rescore').onclick = async () => {
    if (!current) return;
    setText('save_msg', '');
    try {
      const s = await postJson(`/api/manager/clients/${current.user_id}/score`, {});
      currentScore = s;
      setScoreDisplay(s.score);
    } catch (e) {
      setText('save_msg', e.message);
    }
  };

  document.getElementById('btn_save').onclick = async () => {
    if (!current) return;
    if (!editMode) return;
    setText('save_msg', '');
    try {
      const patch = collectForm();
      const upd = await patchJson(`/api/manager/clients/${current.user_id}`, patch);
      setText('save_msg', 'Saved');
      // refresh selected detail and list
      const detail = await getJson(`/api/manager/clients/${current.user_id}`);
      currentDetail = detail;
      editMode = false;
      setHTML('form', renderForm(detail.client, true));
      document.getElementById('btn_save').disabled = true;
      await load();
    } catch (e) {
      setText('save_msg', e.message);
    }
  };
}

main();


