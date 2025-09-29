// static/js/auth.js

// ---------- Small helpers ----------
const $ = (sel) => document.querySelector(sel);

// Get CSRF from cookie or from {% csrf_token %} hidden input in the form
function getCSRFToken() {
  // try cookie first
  const m = document.cookie.match(/(^| )csrftoken=([^;]+)/);
  if (m) return decodeURIComponent(m[2]);
  // fallback: look for hidden input Django adds
  const el = document.querySelector('input[name="csrfmiddlewaretoken"]');
  return el ? el.value : null;
}

// JWT storage
const Tokens = {
  set({ access, refresh }) {
    if (access) localStorage.setItem('access_token', access);
    if (refresh) localStorage.setItem('refresh_token', refresh);
  },
  getAccess()  { return localStorage.getItem('access_token'); },
  getRefresh() { return localStorage.getItem('refresh_token'); },
  clear() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
};

// Keep email during signup flow
const SignupState = {
  setEmail(email) { sessionStorage.setItem('signup_email', email); },
  getEmail()      { return sessionStorage.getItem('signup_email'); },
  clear()         { sessionStorage.removeItem('signup_email'); }
};

// Generic JSON fetch with CSRF + session cookie (needed for OTP flow)
async function apiFetch(url, { method = 'GET', body, auth = false } = {}) {
  const headers = { 'Content-Type': 'application/json' };

  // CSRF for unsafe methods
  if (['POST','PUT','PATCH','DELETE'].includes(method.toUpperCase())) {
    const csrftoken = getCSRFToken();
    if (csrftoken) headers['X-CSRFToken'] = csrftoken;
  }

  if (auth) {
    const token = Tokens.getAccess();
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(url, {
    method,
    headers,
    credentials: 'same-origin', // keep Django session cookie for OTP steps
    body: body ? JSON.stringify(body) : undefined
  });

  let data = null;
  try { data = await res.json(); } catch { /* non-JSON, ignore */ }

  if (!res.ok) {
    const msg = (data && (data.detail || data.error)) || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

// ---------- Page bindings ----------

// 1) SIGNUP PAGE -> send OTP
function bindSignupPage() {
  const form = $('#signup-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = form.email.value.trim();
    if (!email) return alert('Email is required');

    try {
      // pure API: send only email here
      await apiFetch('/users/api/send-otp/', {
        method: 'POST',
        body: { email }
      });
      SignupState.setEmail(email);
      alert('OTP sent to your email');
      // Go to HTML page that contains the OTP form
      window.location.href = `/users/complete-otp/?email=${encodeURIComponent(email)}`;

    } catch (err) {
      alert('Send OTP failed: ' + err.message);
    }
  });
}

// 2) VERIFY OTP PAGE -> verify
function bindVerifyOtpPage() {
  const form = $('#verify-otp-form');
  if (!form) return;

  const emailParam = new URLSearchParams(location.search).get('email');
  const email = emailParam || SignupState.getEmail() || '';
  const emailDisplay = $('#emailDisplay');
  if (emailDisplay) emailDisplay.textContent = email;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const otp = form.otp.value.trim();
    if (!otp) return alert('Enter the OTP');

    try {
      await apiFetch('/users/api/verify-otp/', {
        method: 'POST',
        body: { otp } // backend reads email from session set in send-otp step
      });
      alert('OTP verified!');
      window.location.href = '/users/update-password/';
    } catch (err) {
      alert('Verify OTP failed: ' + err.message);
    }
  });
}

// 3) SET PASSWORD PAGE -> returns JWT
function bindSetPasswordPage() {
  const form = document.getElementById('update-password-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const password = form.password.value;
    const confirm  = form.confirm_password.value;
    if (!password || password !== confirm) return alert('Passwords must match');

    try {
      const data = await apiFetch('/users/api/set-password/', {
        method: 'POST',
        body: { password }
      });
      // API returns { access_token, refresh_token }
      Tokens.set({ access: data.access_token, refresh: data.refresh_token });
      SignupState.clear();
      alert('Signup complete!');
      window.location.href = '/products/dashboard/';
    } catch (err) {
      alert('Set password failed: ' + err.message);
    }
  });
}

// 4) LOGIN PAGE -> JWT via SimpleJWT
function bindLoginPage() {
  const form = document.getElementById('login-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = form.email.value.trim();
    const password = form.password.value;
    if (!email || !password) {
      return alert('Email and password are required');
    }

    try {
      const res = await fetch('/users/api/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) throw new Error('Invalid credentials');

      const data = await res.json();
      Tokens.set({ access: data.access, refresh: data.refresh });

      // Use the next param if present, otherwise fallback
      const params = new URLSearchParams(window.location.search);
      const nextUrl = params.get('next') || '/products/dashboard/';

      window.location.href = nextUrl;
    } catch (err) {
      alert('Login failed: ' + err.message);
    }
  });
}


// 5) FEED GUARD (optional)
function bindFeedGuard() {
  const feedRoot = document.getElementById('feed-root');
  if (!feedRoot) return;

  if (!Tokens.getAccess()) {
    window.location.href = '/users/login/';
    return;
  }

  // Example protected call later:
  // apiFetch('/some/protected/api/', { auth: true })
  //   .then(data => { /* render */ })
  //   .catch(err => {
  //     alert('Failed to load: ' + err.message);
  //     if (/401|403/.test(err.message)) {
  //       Tokens.clear();
  //       window.location.href = '/users/login-page/';
  //     }
  //   });
}

// 6) Logout (optional button with id="logout-btn")
// LOGOUT FUNCTION
function bindLogout() {
  const logoutBtn = document.getElementById("logout-btn");
  if (!logoutBtn) return;

  logoutBtn.addEventListener("click", async () => {
    try {
      const refresh = Tokens.get()?.refresh;
      if (refresh) {
        await apiFetch('/users/api/logout/', {
          method: 'POST',
          body: { refresh }
        });
      }
    } catch (err) {
      console.warn("Logout API error:", err);
    }

    // Always clear tokens client-side
    Tokens.clear();

    // Redirect to login page
    window.location.href = "/users/login/";
  });
}

// Run after DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  bindLogout();
});


// ---------- Init ----------
document.addEventListener('DOMContentLoaded', () => {
  bindSignupPage();
  bindVerifyOtpPage();
  bindSetPasswordPage();
  bindLoginPage();
  bindFeedGuard();
  bindLogout();
});
