// Mobile nav toggle
const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');
if (navToggle) {
  navToggle.addEventListener('click', () => {
    const expanded = navToggle.getAttribute('aria-expanded') === 'true' || false;
    navToggle.setAttribute('aria-expanded', String(!expanded));
    navLinks.classList.toggle('show');
  });
}

// Close nav on link click (mobile)
navLinks?.addEventListener('click', (e) => {
  if (e.target instanceof HTMLAnchorElement) {
    navLinks.classList.remove('show');
    navToggle?.setAttribute('aria-expanded', 'false');
  }
});

// Year in footer
const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = String(new Date().getFullYear());

// Contact form validation and fake submit
const form = document.getElementById('contact-form');
const statusEl = document.getElementById('form-status');

function setError(input, msg) {
  const field = input.closest('.form-field');
  const small = field?.querySelector('.error');
  if (small) small.textContent = msg || '';
  input.setAttribute('aria-invalid', msg ? 'true' : 'false');
}

function validateEmail(email) {
  return /[^\s@]+@[^\s@]+\.[^\s@]+/.test(email);
}

form?.addEventListener('submit', (e) => {
  e.preventDefault();
  if (!(form instanceof HTMLFormElement)) return;

  const submitBtn = form.querySelector('button[type="submit"]');
  const name = form.name.value.trim();
  const email = form.email.value.trim();
  const message = form.message.value.trim();

  let valid = true;
  setError(form.name, '');
  setError(form.email, '');
  setError(form.message, '');

  if (!name) { setError(form.name, 'Please enter your name.'); valid = false; }
  if (!email || !validateEmail(email)) { setError(form.email, 'Please enter a valid email.'); valid = false; }
  if (!message || message.length < 10) { setError(form.message, 'Please share a bit more detail.'); valid = false; }

  if (!valid) return;

  if (submitBtn instanceof HTMLButtonElement) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending…';
  }
  if (statusEl) statusEl.textContent = '';

  // Simulate async send
  setTimeout(() => {
    if (submitBtn instanceof HTMLButtonElement) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Send message';
    }
    if (statusEl) statusEl.textContent = 'Thanks! Your message has been sent.';
    form.reset();
  }, 900);
});
