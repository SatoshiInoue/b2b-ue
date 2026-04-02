import { createOptimizedPicture } from '../../scripts/aem.js';
import { moveInstrumentation } from '../../scripts/scripts.js';

export default function decorate(block) {
  const rows = [...block.querySelectorAll(':scope > div')];
  const getCell = (i) => rows[i]?.querySelector(':scope > div:last-child');

  // ── Background image ──────────────────────────────────────────────────────
  const bgCell = getCell(0);
  const bgImg = bgCell?.querySelector('img');

  const bgDiv = document.createElement('div');
  bgDiv.className = 'hero-b2b-bg';
  if (bgImg) {
    const optimized = createOptimizedPicture(bgImg.src, bgImg.alt || '', false, [
      { media: '(min-width: 900px)', width: '1440' },
      { width: '800' },
    ]);
    // reference field — carries a dynamic data-aue-resource; must use moveInstrumentation
    moveInstrumentation(bgImg, optimized.querySelector('img'));
    bgDiv.append(optimized);
  }

  // ── Content ───────────────────────────────────────────────────────────────
  const contentDiv = document.createElement('div');
  contentDiv.className = 'hero-b2b-content';

  // For each text/richtext cell: create the semantic element, transfer the
  // AEM-injected data-aue-* attributes from the original cell, then set content.
  const preheaderCell = getCell(1);
  if (preheaderCell?.textContent?.trim()) {
    const p = document.createElement('p');
    p.className = 'hero-b2b-preheader';
    moveInstrumentation(preheaderCell, p);
    p.textContent = preheaderCell.textContent.trim();
    contentDiv.append(p);
  }

  const headlineCell = getCell(2);
  const h1 = document.createElement('h1');
  h1.className = 'hero-b2b-headline';
  moveInstrumentation(headlineCell, h1);
  h1.textContent = headlineCell?.textContent?.trim() || '';
  contentDiv.append(h1);

  const descCell = getCell(3);
  const descDiv = document.createElement('div');
  descDiv.className = 'hero-b2b-description';
  // richtext — AEM creates a child node; moveInstrumentation transfers data-aue-resource
  moveInstrumentation(descCell, descDiv);
  descDiv.innerHTML = descCell?.innerHTML || '';
  contentDiv.append(descDiv);

  // ── CTAs ──────────────────────────────────────────────────────────────────
  const cta1TextCell = getCell(4);
  const cta1LinkCell = getCell(5);
  const cta2TextCell = getCell(6);
  const cta2LinkCell = getCell(7);

  const ctasDiv = document.createElement('div');
  ctasDiv.className = 'hero-b2b-ctas';

  const cta1Text = cta1TextCell?.textContent?.trim();
  if (cta1Text) {
    const a = document.createElement('a');
    a.className = 'hero-b2b-cta-primary';
    a.href = cta1LinkCell?.textContent?.trim() || '#';
    a.textContent = cta1Text;
    moveInstrumentation(cta1TextCell, a);
    ctasDiv.append(a);
  }

  const cta2Text = cta2TextCell?.textContent?.trim();
  if (cta2Text) {
    const a = document.createElement('a');
    a.className = 'hero-b2b-cta-secondary';
    a.href = cta2LinkCell?.textContent?.trim() || '#';
    a.textContent = `${cta2Text} →`;
    moveInstrumentation(cta2TextCell, a);
    ctasDiv.append(a);
  }
  contentDiv.append(ctasDiv);

  // ── Stats ─────────────────────────────────────────────────────────────────
  // Stat dividers are CSS ::before pseudo-elements — no extra DOM nodes needed.
  const statsDiv = document.createElement('div');
  statsDiv.className = 'hero-b2b-stats';

  const statPairs = [
    [getCell(8), getCell(9)],
    [getCell(10), getCell(11)],
    [getCell(12), getCell(13)],
  ];

  statPairs.forEach(([valCell, lblCell]) => {
    const val = valCell?.textContent?.trim();
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
  });
  contentDiv.append(statsDiv);

  // ── Assemble ──────────────────────────────────────────────────────────────
  block.textContent = '';
  block.append(bgDiv, contentDiv);
}
