import { moveInstrumentation } from '../../scripts/scripts.js';

export default function decorate(block) {
  const rows = [...block.querySelectorAll(':scope > div')];
  const getText = (i) => rows[i]?.querySelector(':scope > div:last-child')?.textContent?.trim() || '';

  const linkText = getText(0);
  const linkUrl = getText(1) || '#';

  const wrapper = document.createElement('div');
  wrapper.className = 'cta-link-inner';
  wrapper.innerHTML = `<a class="cta-link-anchor" href="${linkUrl}">${linkText} <span class="cta-link-arrow">→</span></a>`;

  rows.forEach((row) => moveInstrumentation(row, wrapper));

  block.textContent = '';
  block.append(wrapper);
}
