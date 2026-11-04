/**
 * In-panel navigation for /gestion/ (ui-crud-pages, design D3/D4/D7).
 *
 * Links marked with `data-panel-link` and POST forms marked with
 * `data-panel-form` are answered by the panel instead of the browser: the
 * request carries `X-Panel-Request: 1` and the response must come back with
 * `X-Panel-View`, otherwise the client simply navigates (session expired,
 * missing permission, or any page it cannot interpret).
 *
 * The URL never changes and no history entry is created.
 */
(() => {
  const PANEL_HEADER = 'X-Panel-Request';
  const VIEW_HEADER = 'X-Panel-View';
  const REDIRECT_HEADER = 'X-Panel-Redirect';

  let inflight = null;

  const activePanel = () =>
    [...document.querySelectorAll('[data-management-panel]')].find((panel) => !panel.hidden);

  const modifiedClick = (event) =>
    event.defaultPrevented ||
    event.button !== 0 ||
    event.metaKey ||
    event.ctrlKey ||
    event.shiftKey ||
    event.altKey;

  function focusHeading(panel) {
    const heading = panel.querySelector('h1, h2');
    if (!heading) return;

    heading.setAttribute('tabindex', '-1');
    heading.focus();
  }

  async function swap(url, init, panel) {
    inflight?.abort();
    const controller = new AbortController();
    inflight = controller;

    panel.setAttribute('aria-busy', 'true');
    panel.innerHTML = '<p class="panel-loading" role="status">Cargando…</p>';

    try {
      const response = await fetch(url, {
        ...init,
        signal: controller.signal,
        headers: { ...(init.headers || {}), [PANEL_HEADER]: '1' },
      });

      if (controller !== inflight) return;

      panel.removeAttribute('aria-busy');

      const view = response.headers.get(VIEW_HEADER);
      if (!response.ok || !view) {
        // 401 (expired session) or a redirect the fetch already followed.
        window.location.assign(response.headers.get(REDIRECT_HEADER) || response.url || url);
        return;
      }

      const html = await response.text();
      if (controller !== inflight) return;

      panel.innerHTML = html;
      focusHeading(panel);
      window.SeatGrid?.init(panel);
    } catch (error) {
      if (error.name === 'AbortError') return;

      panel.removeAttribute('aria-busy');
      window.location.assign(url);
    }
  }

  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[data-panel-link]');
    if (!link || modifiedClick(event)) return;
    if (link.target && link.target !== '_self') return;

    const url = new URL(link.href, window.location.href);
    if (url.origin !== window.location.origin) return;

    const panel = activePanel();
    if (!panel) return;

    event.preventDefault();
    swap(url.pathname + url.search, {}, panel);
  });

  document.addEventListener('submit', (event) => {
    const form = event.target.closest('form[data-panel-form]');
    if (!form || (form.method || 'get').toLowerCase() !== 'post') return;

    const panel = activePanel();
    if (!panel) return;

    event.preventDefault();
    swap(form.action, { method: 'POST', body: new FormData(form) }, panel);
  });
})();
