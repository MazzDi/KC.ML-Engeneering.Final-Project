async function getJson(url) {
  const r = await fetch(url, {credentials: 'include'});
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || data.error || 'Request failed');
  return data;
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

function renderProfile(client) {
  if (!client) return '<div class="muted">—</div>';
  const chunks = [];
  for (const item of FIELD_META) {
    if (item.section) {
      chunks.push(`<div class="section-title">${item.section}</div>`);
      continue;
    }
    const v = client[item.key];
    chunks.push(`<div class="kv-row"><div class="muted">${item.label}</div><div>${v ?? '—'}</div></div>`);
  }
  return chunks.join('');
}

function renderHistory(list) {
  if (!Array.isArray(list) || list.length === 0) return '<div class="muted">—</div>';
  const rows = list
    .slice()
    .sort((a, b) => (a.months_ago ?? 0) - (b.months_ago ?? 0))
    .map((x) => `<tr><td>${x.months_ago}</td><td><span class="pill">${x.status}</span></td></tr>`)
    .join('');
  return `<table class="table"><thead><tr><th>months_ago</th><th>status</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function setText(id, t) {
  const el = document.getElementById(id);
  if (el) el.textContent = t ?? '';
}

function setHTML(id, h) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = h ?? '';
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
  const v = Number.isFinite(proba) ? Math.round((1 - proba) * 100) / 100 : NaN;
  const shown = Number.isFinite(v) ? v.toFixed(2) : '-';
  el.textContent = shown;
  if (Number.isFinite(v)) el.style.color = scoreColor(v);
}

async function logout() {
  await fetch('/auth/logout', {method: 'POST', credentials: 'include'});
  window.location.href = '/';
}

async function load() {
  try {
    const me = await getJson('/auth/me');
    setText('who', `user_id=${me.user_id} role=${me.role}`);
  } catch (_) {
    window.location.href = '/';
    return;
  }

  const dash = await getJson('/api/client/dashboard');
  setHTML('features', renderProfile(dash.client));
  if (dash.manager) {
    setText('manager_info', `Manager: ID:${dash.manager.user_id} ${dash.manager.last_name} ${dash.manager.first_name}`);
  } else {
    setText('manager_info', 'Manager: —');
  }

  setScoreDisplay(dash.score ? dash.score.score : null);
}

async function main() {
  document.getElementById('btn_logout').onclick = logout;
  document.getElementById('btn_score').onclick = async () => {
    setText('score_msg', '');
    try {
      const s = await postJson('/api/client/score', {});
      setScoreDisplay(s.score);
    } catch (e) {
      setText('score_msg', e.message);
    }
  };

  try {
    await load();
  } catch (e) {
    setText('score_msg', e.message);
  }
}

main();


