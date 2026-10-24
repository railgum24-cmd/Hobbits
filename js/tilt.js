/**
 * 3D Perspective Tilt Engine (Эффект физического перевеса при наведении)
 * Реализует эффект, при котором точка под курсором уходит в глубину,
 * а противоположная сторона карточки выплывает вперед.
 * 
 * Perspective Design System
 */

(() => {
  const DEFAULT_MAX_TILT = 10; // максимальный угол наклона в градусах
  const PERSPECTIVE = 900;     // глубина перспективы

  function initTilt(el) {
    if (el._tiltInitialized) return;
    el._tiltInitialized = true;

    el.style.transformStyle = 'preserve-3d';
    el.style.willChange = 'transform';
    el.style.transition = 'transform 0.15s cubic-bezier(0.2, 0.8, 0.4, 1), box-shadow 0.25s ease';

    let bounds = null;

    function onMouseEnter() {
      bounds = el.getBoundingClientRect();
      el.style.transition = 'transform 0.08s ease-out, box-shadow 0.25s ease';
    }

    function onMouseMove(e) {
      if (!bounds) bounds = el.getBoundingClientRect();
      
      const mouseX = e.clientX - bounds.left;
      const mouseY = e.clientY - bounds.top;

      // Нормализуем координаты от -1 до 1 относительно центра карточки
      const xNorm = (mouseX / bounds.width - 0.5) * 2;
      const yNorm = (mouseY / bounds.height - 0.5) * 2;

      // Эффект перевеса наоборот: сторона под курсором плавно приподнимается к пользователю,
      // а противоположная сторона опускается в глубину.
      const rotateX = (-yNorm * DEFAULT_MAX_TILT).toFixed(2);
      const rotateY = (xNorm * DEFAULT_MAX_TILT).toFixed(2);

      el.style.transform = `perspective(${PERSPECTIVE}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.025, 1.025, 1.025)`;
    }

    function onMouseLeave() {
      bounds = null;
      el.style.transition = 'transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease';
      el.style.transform = `perspective(${PERSPECTIVE}px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
    }

    el.addEventListener('mouseenter', onMouseEnter, { passive: true });
    el.addEventListener('mousemove', onMouseMove, { passive: true });
    el.addEventListener('mouseleave', onMouseLeave, { passive: true });
  }

  function autoInit() {
    const selectors = [
      '[data-tilt]',
      '.photo-card',
      '.metric-card',
      '.pillar-card',
      '.diploma-preview-card',
      '.action-tile',
      '.top-card',
      '.cat-card-item'
    ];

    document.querySelectorAll(selectors.join(', ')).forEach(initTilt);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoInit);
  } else {
    autoInit();
  }

  // Наблюдатель за динамически появляющимися элементами
  const observer = new MutationObserver((mutations) => {
    autoInit();
  });

  observer.observe(document.body || document.documentElement, {
    childList: true,
    subtree: true
  });

  window.initTiltElements = autoInit;
})();
