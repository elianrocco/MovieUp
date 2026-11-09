(() => {
  const carousel = document.querySelector('[data-hero-carousel]');
  if (!carousel) return;

  const slides = Array.from(carousel.querySelectorAll('[data-hero-slide]'));
  if (slides.length < 2) return;

  let activeIndex = slides.findIndex((slide) => slide.classList.contains('is-active'));
  if (activeIndex < 0) activeIndex = 0;

  slides.forEach((slide) => {
    slide.addEventListener('transitionend', (event) => {
      if (
        event.target === slide
        && event.propertyName === 'transform'
        && slide.classList.contains('is-exiting')
      ) {
        slide.classList.remove('is-exiting');
        slide.classList.add('is-after');
      }
    });
  });

  window.setInterval(() => {
    const previousSlide = slides[activeIndex];
    const nextIndex = (activeIndex + 1) % slides.length;
    const nextSlide = slides[nextIndex];

    previousSlide.classList.remove('is-active');
    previousSlide.classList.add('is-exiting');
    previousSlide.setAttribute('aria-hidden', 'true');
    previousSlide.inert = true;

    nextSlide.classList.remove('is-after');
    nextSlide.classList.add('is-before');
    void nextSlide.offsetWidth;
    nextSlide.classList.remove('is-before');
    nextSlide.classList.add('is-active');
    nextSlide.setAttribute('aria-hidden', 'false');
    nextSlide.inert = false;

    activeIndex = nextIndex;
  }, 7000);
})();
