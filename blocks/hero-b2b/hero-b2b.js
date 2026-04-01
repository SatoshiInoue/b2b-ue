import { createOptimizedPicture } from '../../scripts/aem.js';
import { moveInstrumentation } from '../../scripts/scripts.js';

export default function decorate(block) {
  const rows = [...block.querySelectorAll(':scope > div')];

  const getCell = (rowIndex) => rows[rowIndex]?.querySelector(':scope > div:last-child');
  const getText = (rowIndex) => getCell(rowIndex)?.textContent?.trim() || '';
  const getLink = (rowIndex) => getCell(rowIndex)?.querySelector('a') || null;

  // Field order matches _hero-b2b.json model
  const bgPicture = getCell(0)?.querySelector('picture');
  const bgImg = bgPicture?.querySelector('img');
  const preheader = getText(1);
  const headline = getText(2);
  const description = getCell(3)?.innerHTML || '';
  const cta1Text = getText(4);
  const cta1Link = getText(5) || '#';
  const cta2Text = getText(6);
  const cta2Link = getText(7) || '#';
  const stat1Value = getText(8);
  const stat1Label = getText(9);
  const stat2Value = getText(10);
  const stat2Label = getText(11);
  const stat3Value = getText(12);
  const stat3Label = getText(13);

  // Build optimized background picture
  let bgEl = '';
  if (bgImg) {
    const optimized = createOptimizedPicture(bgImg.src, bgImg.alt || '', false, [
      { media: '(min-width: 900px)', width: '1440' },
      { width: '800' },
    ]);
    moveInstrumentation(bgImg, optimized.querySelector('img'));
    bgEl = optimized.outerHTML;
  }

  block.innerHTML = `
    <div class="hero-b2b-bg">${bgEl}</div>
    <div class="hero-b2b-overlay"></div>
    <div class="hero-b2b-accent"></div>
    <div class="hero-b2b-content">
      ${preheader ? `<p class="hero-b2b-preheader">${preheader}</p>` : ''}
      <h1 class="hero-b2b-headline">${headline}</h1>
      <div class="hero-b2b-description">${description}</div>
      <div class="hero-b2b-ctas">
        ${cta1Text ? `<a class="hero-b2b-cta-primary" href="${cta1Link}">${cta1Text}</a>` : ''}
        ${cta2Text ? `<a class="hero-b2b-cta-secondary" href="${cta2Link}">${cta2Text} →</a>` : ''}
      </div>
      <div class="hero-b2b-stats">
        ${stat1Value ? `<div class="hero-b2b-stat"><span class="hero-b2b-stat-value">${stat1Value}</span><span class="hero-b2b-stat-label">${stat1Label}</span></div><div class="hero-b2b-stat-divider"></div>` : ''}
        ${stat2Value ? `<div class="hero-b2b-stat"><span class="hero-b2b-stat-value">${stat2Value}</span><span class="hero-b2b-stat-label">${stat2Label}</span></div><div class="hero-b2b-stat-divider"></div>` : ''}
        ${stat3Value ? `<div class="hero-b2b-stat"><span class="hero-b2b-stat-value">${stat3Value}</span><span class="hero-b2b-stat-label">${stat3Label}</span></div>` : ''}
      </div>
    </div>
  `;
}
