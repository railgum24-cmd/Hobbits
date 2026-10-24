/**
 * Модуль анимаций и переходов портала лицея
 * - Приятное размытие при быстром скролле и появление элементов
 * - Кинематографичный портальный переход при авторизации в аккаунт
 * - Плавное появление страниц без резких скачков
 */

const Transitions = (() => {

  // Плавный переход при авторизации
  function portalNavigate(targetUrl, buttonElement) {
    if (buttonElement) {
      buttonElement.disabled = true;
      buttonElement.innerHTML = `
        <span style="display:inline-flex; align-items:center; gap:8px;">
          <span class="btn-spinner"></span>
          <span>Вход в защищённый реестр...</span>
        </span>
      `;
      buttonElement.style.boxShadow = '0 0 24px rgba(0, 189, 125, 0.6)';
    }

    // Создаём слой портального перехода
    let overlay = document.getElementById('portal-transition-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'portal-transition-overlay';
      overlay.className = 'portal-transition-curtain';
      document.body.appendChild(overlay);
    }

    // Запуск анимации перехода
    requestAnimationFrame(() => {
      overlay.classList.add('active');
      setTimeout(() => {
        window.location.href = targetUrl;
      }, 420);
    });
  }

  // Приятное размытие фона при активном скролле
  function initScrollBlur() {
    let scrollTimeout = null;
    let lastScrollY = window.scrollY;

    const blurBar = document.createElement('div');
    blurBar.className = 'scroll-motion-blur';
    document.body.appendChild(blurBar);

    window.addEventListener('scroll', () => {
      const currentScrollY = window.scrollY;
      const speed = Math.abs(currentScrollY - lastScrollY);
      lastScrollY = currentScrollY;

      if (speed > 16) {
        blurBar.classList.add('visible');
      }

      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        blurBar.classList.remove('visible');
      }, 90);
    }, { passive: true });
  }

  // Плавное появление секций при прокрутке
  function initScrollReveal() {
    if (!('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.08,
      rootMargin: '0px 0px -40px 0px'
    });

    document.querySelectorAll('.landing-section, .pillar-card, .photo-card, .metric-card, .action-tile, .panel').forEach(el => {
      el.classList.add('reveal-on-scroll');
      observer.observe(el);
    });
  }

  // Инициализация при загрузке документа
  document.addEventListener('DOMContentLoaded', () => {
    document.body.classList.add('page-loaded');
    initScrollBlur();
    initScrollReveal();
  });

  return { portalNavigate };
})();
