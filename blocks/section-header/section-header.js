import { moveInstrumentation } from '../../scripts/scripts.js';

export default function decorate(block) {
  const rows = [...block.querySelectorAll(':scope > div')];
  const getText = (i) => rows[i]?.querySelector(':scope > div:last-child')?.textContent?.trim() || '';
  const getHTML = (i) => rows[i]?.querySelector(':scope > div:last-child')?.innerHTML || '';

  const eyebrow = getText(0);
  const heading = getText(1);
  const subtitle = getHTML(2);

  const el = document.createElement('div');
  el.className = 'section-header-inner';
  el.innerHTML = `
    ${eyebrow ? `<p class="section-header-eyebrow"><span class="section-header-line"></span>${eyebrow}<span class="section-header-line"></span></p>` : ''}
    ${heading ? `<h2 class="section-header-heading">${heading}</h2>` : ''}
    ${subtitle ? `<div class="section-header-subtitle">${subtitle}</div>` : ''}
  `;

  // Preserve UE instrumentation from each source row onto the new element
  rows.forEach((row) => moveInstrumentation(row, el));

  block.textContent = '';
  block.append(el);
}
