(() => {
  const tabs = Array.from(document.querySelectorAll('[data-management-tab]'));
  const panels = Array.from(document.querySelectorAll('[data-management-panel]'));

  if (!tabs.length || !panels.length) return;

  function activateTab(name) {
    tabs.forEach((tab) => {
      const active = tab.dataset.managementTab === name;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-pressed', String(active));
    });

    panels.forEach((panel) => {
      panel.hidden = panel.dataset.managementPanel !== name;
    });
  }

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => activateTab(tab.dataset.managementTab));
  });
})();
