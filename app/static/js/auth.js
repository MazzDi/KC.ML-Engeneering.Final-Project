async function postJson(url, body) {
  const r = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    credentials: 'include',
    body: JSON.stringify(body),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    const msg = data.detail || data.error || 'Request failed';
    throw new Error(msg);
  }
  return data;
}

function setMsg(text) {
  const el = document.getElementById('msg');
  if (el) el.textContent = text || '';
}

async function main() {
  const btn = document.getElementById('btn_login');
  btn.onclick = async () => {
    setMsg('');
    const login = document.getElementById('login').value.trim();
    const password = document.getElementById('password').value;
    if (!login || !password) return setMsg('Введите login и пароль');
    try {
      const res = await postJson('/auth/login', {login, password});
      window.location.href = res.redirect || '/ui';
    } catch (e) {
      setMsg(e.message);
    }
  };
}

main();


