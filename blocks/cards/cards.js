import { createOptimizedPicture } from '../../scripts/aem.js';
import { moveInstrumentation } from '../../scripts/scripts.js';

const ICONS = {
  'hex-tolerance': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12,2 21,7 21,17 12,22 3,17 3,7"/><circle cx="12" cy="12" r="3"/></svg>`,
  clipboard: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/><path d="M9 12h6M9 16h4"/></svg>`,
  waveform: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h3l3-7 4 14 3-7 3 4 2-4h2"/></svg>`,
  monitor: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>`,
  lock: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/></svg>`,
  cube: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><path d="M3.27 6.96L12 12.01l8.73-5.05M12 22.08V12"/></svg>`,
};

export default function decorate(block) {
  const ul = document.createElement('ul');
  [...block.children].forEach((row) => {
    const li = document.createElement('li');

    // row.children[2] = cardstyle, row.children[3] = ctastyle, row.children[4] = icon
    const cardStyle = row.children[2]?.querySelector('p')?.textContent?.trim() || '';
    const ctaStyle = row.children[3]?.querySelector('p')?.textContent?.trim() || '';
    const iconKey = row.children[4]?.querySelector('p')?.textContent?.trim() || '';

    if (cardStyle) li.className = cardStyle;

    moveInstrumentation(row, li);
    while (row.firstElementChild) li.append(row.firstElementChild);

    [...li.children].forEach((div, index) => {
      if (index === 0) div.className = 'cards-card-image';
      else if (index === 1) div.className = 'cards-card-body';
      else {
        div.className = 'cards-config';
        const p = div.querySelector('p');
        if (p) p.style.display = 'none';
      }
    });

    // Apply CTA style to button containers
    li.querySelectorAll('p.button-container').forEach((bp) => {
      bp.classList.remove('default', 'cta-button', 'cta-button-secondary', 'cta-button-dark', 'cta-default');
      if (ctaStyle) bp.classList.add(ctaStyle);
    });

    // Inject icon for solution-tile style
    if (cardStyle === 'solution-tile' && iconKey && ICONS[iconKey]) {
      const iconEl = document.createElement('div');
      iconEl.className = 'cards-card-icon';
      iconEl.innerHTML = ICONS[iconKey];
      li.append(iconEl);
    }

    ul.append(li);
  });

  ul.querySelectorAll('picture > img').forEach((img) => {
    const optimizedPic = createOptimizedPicture(img.src, img.alt, false, [{ width: '750' }]);
    moveInstrumentation(img, optimizedPic.querySelector('img'));
    img.closest('picture').replaceWith(optimizedPic);
  });

  block.textContent = '';
  block.append(ul);
}
