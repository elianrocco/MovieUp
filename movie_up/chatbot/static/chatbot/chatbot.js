(() => {
  const widget = document.getElementById('chatbot-widget');
  if (!widget) return;

  const launcher = document.getElementById('chatbot-launcher');
  const panel = document.getElementById('chatbot-panel');
  const closeButton = document.getElementById('chatbot-close');
  const messages = document.getElementById('chatbot-messages');
  const form = document.getElementById('chatbot-form');
  const input = document.getElementById('chatbot-question');
  const submitButton = document.getElementById('chatbot-submit');
  const header = document.getElementById('site-header');
  const managementSubnav = document.querySelector('.management-subnav');
  const footer = document.getElementById('site-footer');
  const conversation = [];
  let pending = false;

  const updateGeometry = () => {
    const navigationBottoms = [header, managementSubnav]
      .filter(Boolean)
      .map((navigation) => navigation.getBoundingClientRect().bottom);
    const headerBottom = Math.max(0, ...navigationBottoms);
    const footerTop = footer
      ? footer.getBoundingClientRect().top
      : window.innerHeight;
    const footerObstruction = Math.max(0, window.innerHeight - footerTop);

    widget.style.setProperty('--chatbot-header-bottom', `${headerBottom}px`);
    widget.style.setProperty(
      '--chatbot-footer-obstruction',
      `${footerObstruction}px`,
    );
  };

  const observers = [];
  if ('ResizeObserver' in window) {
    const observer = new ResizeObserver(updateGeometry);
    if (header) observer.observe(header);
    if (managementSubnav) observer.observe(managementSubnav);
    if (footer) observer.observe(footer);
    observers.push(observer);
  }
  window.addEventListener('resize', updateGeometry, { passive: true });
  window.addEventListener('scroll', updateGeometry, { passive: true });
  updateGeometry();

  const setOpen = (open) => {
    panel.hidden = !open;
    launcher.hidden = open;
    panel.setAttribute('aria-hidden', String(!open));
    launcher.setAttribute('aria-expanded', String(open));
    if (open) input.focus();
    else launcher.focus();
    updateGeometry();
  };

  launcher.addEventListener('click', () => setOpen(panel.hidden));
  closeButton.addEventListener('click', () => setOpen(false));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !panel.hidden) setOpen(false);
  });

  const appendMessage = (role, text, modifier = '') => {
    const article = document.createElement('article');
    article.className = `chatbot-message chatbot-message--${role}${modifier ? ` chatbot-message--${modifier}` : ''}`;
    article.setAttribute('data-chatbot-transcript-message', 'true');
    const label = document.createElement('p');
    label.className = 'chatbot-message__label';
    label.textContent = role === 'user' ? 'Vos' : 'MovieUp';
    const body = document.createElement('p');
    body.textContent = text;
    article.append(label, body);
    messages.append(article);
    messages.scrollTop = messages.scrollHeight;
    return article;
  };

  const sendQuestion = async (rawQuestion) => {
    const question = rawQuestion.trim();
    if (!question || pending) return;

    const history = conversation.slice(-10);
    conversation.push({ role: 'user', content: question });
    appendMessage('user', question);
    input.value = '';
    pending = true;
    submitButton.disabled = true;
    const loading = appendMessage('assistant', 'Pensando…', 'loading');
    loading.setAttribute('role', 'status');

    try {
      const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]').value;
      const response = await fetch('/chatbot/api/preguntar/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ question, history }),
      });
      const payload = await response.json();
      loading.remove();
      if (!response.ok) {
        appendMessage('error', payload.error || 'No se pudo obtener una respuesta.');
        return;
      }

      conversation.push({ role: 'assistant', content: payload.answer });
      appendMessage('assistant', payload.answer);
    } catch (_error) {
      loading.remove();
      appendMessage('error', 'No se pudo conectar con el asistente. Intentá nuevamente.');
    } finally {
      pending = false;
      submitButton.disabled = false;
      input.focus();
    }
  };

  messages.addEventListener('click', (event) => {
    const suggestion = event.target.closest('[data-chatbot-question]');
    if (suggestion) sendQuestion(suggestion.dataset.chatbotQuestion);
  });

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    sendQuestion(input.value);
  });

  input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });
})();
