import { getMetadata } from '../../scripts/aem.js';
import { loadFragment } from '../fragment/fragment.js';
import { isAuthorEnvironment } from '../../scripts/scripts.js';

import {
  getLanguage, getSiteName, PATH_PREFIX,
} from '../../scripts/utils.js';

/**
 * loads and decorates the footer
 * @param {Element} block The footer block element
 */
export default async function decorate(block) {
  const footerMeta = getMetadata('footer');
  const langCode = getLanguage();
  const siteName = await getSiteName();
  const isAuthor = isAuthorEnvironment();
  let footerPath = `/${langCode}/footer`;

  if (isAuthor) {
    footerPath = footerMeta
      ? new URL(footerMeta, window.location).pathname
      : `/content/${siteName}${PATH_PREFIX}/${langCode}/footer`;
  }

  const fragment = await loadFragment(footerPath);

  // decorate footer DOM
  block.textContent = '';
  const footer = document.createElement('div');
  footer.className = 'footer-wrapper';
  while (fragment.firstElementChild) footer.append(fragment.firstElementChild);

  // Assign named classes to the first 3 sections
  const sections = [...footer.children];
  const sectionClasses = ['footer-brand', 'footer-nav', 'footer-bottom'];
  sections.forEach((section, i) => {
    if (i < sectionClasses.length) {
      section.classList.add(sectionClasses[i]);
    }
  });

  // Prepend logo to the brand section
  const brandSection = footer.querySelector('.footer-brand');
  if (brandSection) {
    const logoLink = document.createElement('a');
    logoLink.className = 'footer-logo-link';
    logoLink.href = `/${langCode}`;

    const logoImg = document.createElement('img');
    logoImg.src = '/icons/logo.svg';
    logoImg.alt = '';
    logoImg.width = 32;
    logoImg.height = 32;
    logoImg.className = 'footer-logo-mark';
    logoImg.setAttribute('aria-hidden', 'true');

    const logoName = document.createElement('span');
    logoName.className = 'footer-logo-name';
    logoName.textContent = 'LUMINA NOVENTIS';

    logoLink.append(logoImg, logoName);
    brandSection.prepend(logoLink);
  }

  block.append(footer);
}
