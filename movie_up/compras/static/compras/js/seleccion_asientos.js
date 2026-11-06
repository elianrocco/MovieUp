(() => {
    const SELECTED_CLASS = 'celda--seleccionada';

    function formatTotal(centavos) {
        return `$${(centavos / 100).toFixed(2)}`;
    }

    /**
     * Wire the seat selection form found under `root`. Seat buttons toggle a
     * selected state, keep the hidden `celda` inputs in sync and update the
     * counter, the total (computed in integer cents) and the confirm button.
     * Returns false when there is no form or when it is already wired.
     */
    function init(root = document) {
        const form = root.querySelector('[data-compra-form]');
        const grid = root.querySelector('[data-compra-grid]');
        if (!form || !grid || form.dataset.ready === '1') {
            return false;
        }

        form.dataset.ready = '1';

        const contador = form.querySelector('[data-contador]');
        const total = form.querySelector('[data-total]');
        const confirmar = form.querySelector('[data-confirmar]');
        const precioCentavos = Math.round(Number(form.dataset.precio) * 100);

        const seleccionadas = () =>
            [...grid.querySelectorAll('button[data-asiento]')].filter((celda) =>
                celda.classList.contains(SELECTED_CLASS),
            );

        const sincronizar = () => {
            const elegidas = seleccionadas();

            contador.textContent = String(elegidas.length);
            total.textContent = formatTotal(precioCentavos * elegidas.length);

            form.querySelectorAll('input[name="celda"]').forEach((input) => input.remove());
            elegidas.forEach((celda) => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'celda';
                input.value = `${celda.dataset.fila}:${celda.dataset.asiento}`;
                form.append(input);
            });

            const habilitado = elegidas.length > 0;
            confirmar.disabled = !habilitado;
            confirmar.setAttribute('aria-disabled', String(!habilitado));
            confirmar.classList.toggle('btn--sold-out', !habilitado);
        };

        grid.addEventListener('click', (event) => {
            const celda = event.target.closest('button[data-asiento]');
            if (!celda || !grid.contains(celda)) {
                return;
            }

            const seleccionada = celda.classList.toggle(SELECTED_CLASS);
            celda.setAttribute('aria-pressed', String(seleccionada));
            sincronizar();
        });

        sincronizar();
        return true;
    }

    window.SeleccionAsientos = { init };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => init(document));
    } else {
        init(document);
    }
})();
