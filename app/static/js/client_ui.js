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

function kv(obj) {
  if (!obj) return '<div class="muted">—</div>';
  return Object.entries(obj)
    .map(([k, v]) => `<div class="kv-row"><div class="muted">${k}</div><div>${v ?? '—'}</div></div>`)
    .join('');
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
  setHTML('features', kv(dash.client));
  setText('manager', dash.manager ? `manager_id=${dash.manager.user_id}` : '—');
  setHTML('credit', dash.credit ? kv({amount_total: dash.credit.amount_total, annual_rate: dash.credit.annual_rate}) : '<div class="muted">—</div>');
  setHTML('history', dash.credit ? renderHistory(dash.credit.payment_history) : '<div class="muted">—</div>');

  if (dash.score) {
    setText('score_value', String(dash.score.score));
    document.getElementById('btn_score').disabled = true;
  } else {
    setText('score_value', '—');
    document.getElementById('btn_score').disabled = false;
  }
}

async function main() {
  document.getElementById('btn_logout').onclick = logout;
  document.getElementById('btn_score').onclick = async () => {
    setText('score_msg', '');
    try {
      const s = await postJson('/api/client/score', {});
      setText('score_value', String(s.score));
      document.getElementById('btn_score').disabled = true;
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


