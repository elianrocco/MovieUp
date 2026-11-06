(() => {
  const root = document.querySelector('[data-statistics]');
  if (!root) return;

  const button = root.querySelector('[data-stats-switch]');
  const label = root.querySelector('[data-stats-period-label]');
  const sections = Array.from(root.querySelectorAll('[data-stats-period]'));
  const periods = ['semanal', 'mensual', 'anual'];
  const periodLabels = {
    semanal: 'Semanal',
    mensual: 'Mensual',
    anual: 'Anual',
  };

  if (!button || !label || !sections.length) return;

  let activeIndex = 0;

  function showPeriod(period) {
    sections.forEach((section) => {
      section.hidden = section.dataset.statsPeriod !== period;
    });
    button.dataset.currentPeriod = period;
    label.textContent = periodLabels[period];
    button.setAttribute(
      'aria-label',
      `Cambiar periodo; modo actual: ${periodLabels[period].toLowerCase()}`,
    );
  }

  button.addEventListener('click', () => {
    activeIndex = (activeIndex + 1) % periods.length;
    showPeriod(periods[activeIndex]);
  });

  showPeriod(periods[activeIndex]);
})();
