(() => {
  function addPhoto(container, className, word, before) {
    const source = window.REAL_PHOTOS?.[word];
    if (!source || container.querySelector(`.${className}`)) return;
    const image = document.createElement('img');
    image.className = className;
    image.src = source;
    image.alt = word;
    image.loading = 'lazy';
    image.onerror = () => image.remove();
    container.insertBefore(image, before || null);
  }

  function decorate() {
    document.querySelectorAll('.letter-card').forEach(card => {
      const word = card.querySelector('strong')?.nextElementSibling?.textContent.trim();
      addPhoto(card, 'word-thumb', word, card.querySelector('strong'));
    });
    document.querySelectorAll('.detail-copy').forEach(copy => {
      addPhoto(copy, 'word-illustration', copy.querySelector('.example-word')?.textContent.trim(), copy.querySelector('.example-word'));
    });
    document.querySelectorAll('.featured-card').forEach(card => {
      addPhoto(card, 'featured-thumb', card.querySelector('strong')?.textContent.trim(), card.querySelector('strong'));
    });
  }

  new MutationObserver(decorate).observe(document.body, { childList: true, subtree: true });
  decorate();
})();
