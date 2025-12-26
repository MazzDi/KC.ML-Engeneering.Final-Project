async function getJson(url) {
  const r = await fetch(url, {credentials: 'include'});
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

async function main() {
  document.getElementById('btn_logout').onclick = logout;
  try {
    const me = await getJson('/auth/me');
    setText('who', `user_id=${me.user_id} role=${me.role}`);
    const credit = await getJson('/api/client/credit');
    if (!credit) {
      setHTML('credit', '<div class="muted">Нет активного кредита</div>');
      setHTML('history', '<div class="muted">—</div>');
      return;
    }
    setHTML('credit', kv({amount_total: credit.amount_total, annual_rate: credit.annual_rate}));
    setHTML('history', renderHistory(credit.payment_history));
  } catch (e) {
    setText('msg', e.message);
  }
}

main();


