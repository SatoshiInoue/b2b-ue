import { createOptimizedPicture } from '../../scripts/aem.js';
import { moveInstrumentation } from '../../scripts/scripts.js';

export default function decorate(block) {
  const rows = [...block.querySelectorAll(':scope > div')];

  // Returns the value cell (second div) of a row — carries data-aue-prop
  // attributes injected by AEM for UE inline editing.
  const getCell = (i) => rows[i]?.querySelector(':scope > div:last-child');

  // Field order matches _hero-b2b.json / models/_component-models.json
  const imageCell = getCell(0);
  const preheaderCell = getCell(1);
  const headlineCell = getCell(2);
  const descriptionCell = getCell(3);
  const cta1TextCell = getCell(4);
  const cta1LinkCell = getCell(5);
  const cta2TextCell = getCell(6);
  const cta2LinkCell = getCell(7);
  const stat1ValueCell = getCell(8);
  const stat1LabelCell = getCell(9);
  const stat2ValueCell = getCell(10);
  const stat2LabelCell = getCell(11);
  const stat3ValueCell = getCell(12);
  const stat3LabelCell = getCell(13);

  // ── Background image ──────────────────────────────────────────────────────
  const bgImg = imageCell?.querySelector('img');
  const bgDiv = document.createElement('div');
  bgDiv.className = 'hero-b2b-bg';
  if (bgImg) {
    const optimized = createOptimizedPicture(bgImg.src, bgImg.alt || '', false, [
      { media: '(min-width: 900px)', width: '1440' },
      { width: '800' },
    ]);
    moveInstrumentation(bgImg, optimized.querySelector('img'));
    bgDiv.append(optimized);
  }

  // ── Overlay + accent ──────────────────────────────────────────────────────
  const overlayDiv = document.createElement('div');
  overlayDiv.className = 'hero-b2b-overlay';
  const accentDiv = document.createElement('div');
  accentDiv.className = 'hero-b2b-accent';

  // ── Content ───────────────────────────────────────────────────────────────
  const contentDiv = document.createElement('div');
  contentDiv.className = 'hero-b2b-content';

  // Helper: create a plain text element and move UE instrumentation from
  // the original value cell so the element is inline-editable in UE.
  function makeText(tag, cls, cell) {
    const el = document.createElement(tag);
    el.className = cls;
    el.textContent = cell?.textContent?.trim() || '';
    if (cell) moveInstrumentation(cell, el);
    return el;
  }

  // Preheader
  const preheaderText = preheaderCell?.textContent?.trim() || '';
  if (preheaderText) {
    contentDiv.append(makeText('p', 'hero-b2b-preheader', preheaderCell));
  }

  // Headline
  contentDiv.append(makeText('h1', 'hero-b2b-headline', headlineCell));

  // Description (richtext — keep inner HTML, moveInstrumentation on the cell)
  const descDiv = document.createElement('div');
  descDiv.className = 'hero-b2b-description';
  descDiv.innerHTML = descriptionCell?.innerHTML || '';
  if (descriptionCell) moveInstrumentation(descriptionCell, descDiv);
  contentDiv.append(descDiv);

  // CTAs
  const ctasDiv = document.createElement('div');
  ctasDiv.className = 'hero-b2b-ctas';

  const cta1Text = cta1TextCell?.textContent?.trim() || '';
  if (cta1Text) {
    const a1 = document.createElement('a');
    a1.className = 'hero-b2b-cta-primary';
    a1.href = cta1LinkCell?.textContent?.trim() || '#';
    a1.textContent = cta1Text;
    moveInstrumentation(cta1TextCell, a1);
    ctasDiv.append(a1);
  }

  const cta2Text = cta2TextCell?.textContent?.trim() || '';
  if (cta2Text) {
    const a2 = document.createElement('a');
    a2.className = 'hero-b2b-cta-secondary';
    a2.href = cta2LinkCell?.textContent?.trim() || '#';
    a2.textContent = `${cta2Text} →`;
    moveInstrumentation(cta2TextCell, a2);
    ctasDiv.append(a2);
  }

  contentDiv.append(ctasDiv);

  // Stats
  const statsDiv = document.createElement('div');
  statsDiv.className = 'hero-b2b-stats';

  [[stat1ValueCell, stat1LabelCell], [stat2ValueCell, stat2LabelCell], [stat3ValueCell, stat3LabelCell]]
    .forEach(([valCell, lblCell], i) => {
      const val = valCell?.textContent?.trim() || '';
      if (!val) return;

      const statDiv = document.createElement('div');
      statDiv.className = 'hero-b2b-stat';

      const valSpan = document.createElement('span');
      valSpan.className = 'hero-b2b-stat-value';
      valSpan.textContent = val;
      moveInstrumentation(valCell, valSpan);

      const lblSpan = document.createElement('span');
      lblSpan.className = 'hero-b2b-stat-label';
      lblSpan.textContent = lblCell?.textContent?.trim() || '';
      moveInstrumentation(lblCell, lblSpan);

      statDiv.append(valSpan, lblSpan);
      statsDiv.append(statDiv);

      if (i < 2) {
        const divider = document.createElement('div');
        divider.className = 'hero-b2b-stat-divider';
        statsDiv.append(divider);
      }
    });

  contentDiv.append(statsDiv);

  // ── Replace block contents ────────────────────────────────────────────────
  block.innerHTML = '';
  block.append(bgDiv, overlayDiv, accentDiv, contentDiv);
}
