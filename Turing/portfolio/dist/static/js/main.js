/**
 * Interactive Client Scripts for Developer Portfolio
 * -------------------------------------------------
 * Handles theme switching, dynamic typewriter, project category filtering,
 * smooth scrolling, mobile nav, and contact form validation.
 */

document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  initTypewriter();
  initProjectFilters();
  initMobileNav();
  initScrollSpyAndBackToTop();
  initContactForm();
});

/* ==========================================================================
   1. Theme Toggle (Dark / Light)
   ========================================================================== */
function initThemeToggle() {
  const toggleBtn = document.getElementById('theme-toggle');
  if (!toggleBtn) return;

  const savedTheme = localStorage.getItem('portfolio-theme') ||
    (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');

  document.documentElement.setAttribute('data-theme', savedTheme);

  toggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('portfolio-theme', newTheme);
  });
}

/* ==========================================================================
   2. Dynamic Typewriter Effect
   ========================================================================== */
function initTypewriter() {
  const el = document.getElementById('typewriter');
  if (!el) return;

  let phrases = [];
  try {
    const raw = el.getAttribute('data-phrases');
    // Normalize single quotes or JSON
    phrases = JSON.parse(raw.replace(/'/g, '"'));
  } catch (err) {
    phrases = ['Python Developer', 'Backend Architect', 'Data Engineer'];
  }

  if (!phrases.length) return;

  let phraseIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  const typingSpeed = 75;
  const deletingSpeed = 40;
  const pauseEnd = 2000;
  const pauseStart = 400;

  function type() {
    const currentPhrase = phrases[phraseIndex];

    if (isDeleting) {
      el.textContent = currentPhrase.substring(0, charIndex - 1);
      charIndex--;
    } else {
      el.textContent = currentPhrase.substring(0, charIndex + 1);
      charIndex++;
    }

    let delay = isDeleting ? deletingSpeed : typingSpeed;

    if (!isDeleting && charIndex === currentPhrase.length) {
      delay = pauseEnd;
      isDeleting = true;
    } else if (isDeleting && charIndex === 0) {
      isDeleting = false;
      phraseIndex = (phraseIndex + 1) % phrases.length;
      delay = pauseStart;
    }

    setTimeout(type, delay);
  }

  type();
}

/* ==========================================================================
   3. Project Category Filter
   ========================================================================== */
function initProjectFilters() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const projectCards = document.querySelectorAll('.project-card');

  if (!filterBtns.length || !projectCards.length) return;

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const selectedCategory = btn.getAttribute('data-filter');

      projectCards.forEach(card => {
        const cardCategory = card.getAttribute('data-category');
        if (selectedCategory === 'All' || cardCategory === selectedCategory) {
          card.style.display = 'flex';
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'scale(1)';
          }, 10);
        } else {
          card.style.opacity = '0';
          card.style.transform = 'scale(0.95)';
          setTimeout(() => {
            card.style.display = 'none';
          }, 200);
        }
      });
    });
  });
}

/* ==========================================================================
   4. Mobile Navigation Drawer
   ========================================================================== */
function initMobileNav() {
  const hamburger = document.getElementById('hamburger-btn');
  const navMenu = document.getElementById('nav-menu');
  const navLinks = document.querySelectorAll('.nav-link');

  if (!hamburger || !navMenu) return;

  hamburger.addEventListener('click', () => {
    navMenu.classList.toggle('open');
  });

  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      navMenu.classList.remove('open');
    });
  });
}

/* ==========================================================================
   5. ScrollSpy & Back to Top Button
   ========================================================================== */
function initScrollSpyAndBackToTop() {
  const backToTopBtn = document.getElementById('back-to-top');
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');

  window.addEventListener('scroll', () => {
    const scrollY = window.pageYOffset;

    // Back to top visibility
    if (backToTopBtn) {
      if (scrollY > 400) {
        backToTopBtn.classList.add('visible');
      } else {
        backToTopBtn.classList.remove('visible');
      }
    }

    // ScrollSpy active link highlight
    sections.forEach(current => {
      const sectionHeight = current.offsetHeight;
      const sectionTop = current.offsetTop - 120;
      const sectionId = current.getAttribute('id');

      if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
          }
        });
      }
    });
  });

  if (backToTopBtn) {
    backToTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
}

/* ==========================================================================
   6. Contact Form Submission Handling
   ========================================================================== */
function initContactForm() {
  const form = document.getElementById('contact-form');
  const submitBtn = document.getElementById('submit-btn');
  const alertBox = document.getElementById('form-alert');

  if (!form || !submitBtn || !alertBox) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const name = form.elements['name'].value.trim();
    const email = form.elements['email'].value.trim();
    const subject = form.elements['subject'].value;
    const message = form.elements['message'].value.trim();

    if (!name || !email || !message) {
      showAlert('Please fill in all required fields.', 'error');
      return;
    }

    // Toggle button state to loading
    const btnText = submitBtn.querySelector('.btn-text');
    const btnSpinner = submitBtn.querySelector('.btn-spinner');
    if (btnText) btnText.classList.add('hidden');
    if (btnSpinner) btnSpinner.classList.remove('hidden');
    submitBtn.disabled = true;

    // Simulate sending message or fallback to mailto
    setTimeout(() => {
      if (btnText) btnText.classList.remove('hidden');
      if (btnSpinner) btnSpinner.classList.add('hidden');
      submitBtn.disabled = false;

      // Construct a clean mailto backup so user can also send from their client
      const mailtoSubject = encodeURIComponent(`[Portfolio Inquiry] ${subject} from ${name}`);
      const mailtoBody = encodeURIComponent(`Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`);
      const mailtoLink = `mailto:alex.morgan.dev@example.com?subject=${mailtoSubject}&body=${mailtoBody}`;

      showAlert(
        `Thank you, ${name}! Your inquiry has been prepared. If your email client does not open automatically, <a href="${mailtoLink}" style="text-decoration:underline; font-weight:600;">click here to send via mail</a>.`,
        'success'
      );

      form.reset();
    }, 800);
  });

  function showAlert(msg, type) {
    alertBox.innerHTML = msg;
    alertBox.className = `form-alert ${type}`;
    alertBox.classList.remove('hidden');

    setTimeout(() => {
      // Keep alert visible for 8 seconds
      setTimeout(() => {
        alertBox.classList.add('hidden');
      }, 8000);
    }, 100);
  }
}
