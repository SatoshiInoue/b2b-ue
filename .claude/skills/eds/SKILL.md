---
name: eds
description: AEM Edge Delivery Services (EDS) + Universal Editor (XWalk) development assistant for the finehotel-ue project. Use this skill whenever the user wants to: create or customize a block (JS decorator, CSS, JSON), edit component models or definitions, add fields to the Universal Editor property panel, change theming or CSS variables, update component filters, or run the JSON build pipeline. Trigger on phrases like "add a block", "new block", "customize hero", "add a field", "change theme", "edit model", "update filter", "build json", or anything related to AEM EDS block development.
---

# AEM EDS / XWalk Development Skill

Full documentation is in `docs/` (English) and `docs/ja/` (Japanese).

## Quick Reference

**Build command — run after any `_*.json` change:**
```bash
npm run build:json
```

**Never edit root `component-*.json`** — always edit source files in `models/` or `blocks/{name}/_{name}.json`.

---

## Workflow by Task

### Create a new block

1. Read `blocks/hero/hero.js` and `blocks/cards/cards.js` as pattern references
2. Create `blocks/{name}/{name}.js` — `export default function decorate(block) { ... }`
3. Create `blocks/{name}/{name}.css`
4. Create `blocks/{name}/_{name}.json` — definitions + models + filters
5. Add block name to `section` filter in `models/_component-filters.json`
6. Run `npm run build:json`

See `docs/block-development.md` for full patterns and field type reference.

### Add/edit a field in Universal Editor

Edit `blocks/{name}/_{name}.json` → `models` section. For shared models (page-metadata, image, title), edit `models/_component-models.json`. Run `npm run build:json`.

See `docs/component-models.md` for all field component types.

### Add a new theme

1. Add `body.{theme-name} { --brand-*: ...; }` to `styles/styles.css`
2. Add `{ "name": "...", "value": "{theme-name}" }` to the `theme` select in `models/_component-models.json` **and** `models/_page.json` (both files)
3. Run `npm run build:json`

See `docs/theming.md` for CSS variable reference.

### Add a layout variant to an existing block (e.g. Hero)

1. Add option to the select field in `blocks/{name}/_{name}.json`
2. Add CSS for `.{block-name}.{variant-value} { ... }` in `{name}.css`
3. Run `npm run build:json` — no JS change needed if the decorator already does `block.classList.add(value)`

---

## Key Patterns

### Reading a config field and applying as CSS class

```javascript
export default function decorate(block) {
  const value = block.querySelector(':scope div:nth-child(N) > div')?.textContent?.trim() || 'default';
  block.classList.add(value);
  block.querySelector(':scope div:nth-child(N)')?.style.setProperty('display', 'none');
}
```

### Restructuring DOM — always use `moveInstrumentation`

```javascript
import { moveInstrumentation } from '../../scripts/scripts.js';

const li = document.createElement('li');
moveInstrumentation(row, li); // preserves data-aue-* attributes for Universal Editor
while (row.firstElementChild) li.append(row.firstElementChild);
```

### CRITICAL: making ALL fields inline-editable in Universal Editor

AEM injects `data-aue-prop` / `data-aue-type` / `data-aue-label` attributes onto each
field's **value cell** (second `<div>` of each row) at server-render time:
- `reference` and `richtext` fields → get `data-aue-resource` (child JCR node) → appear in the UE content tree automatically
- `text`, `select`, `boolean`, `number` fields → get `data-aue-prop` on the value cell → only editable inline if you transfer those attributes to the new DOM element

**If you use `block.innerHTML = ...` or discard the original rows without calling
`moveInstrumentation`, all text/select/boolean fields lose their edit handles and
become invisible to Universal Editor.** This is the #1 cause of "I can only edit
image and description" complaints.

The correct pattern — use DOM construction + `moveInstrumentation` for every field:

```javascript
import { moveInstrumentation } from '../../scripts/scripts.js';

export default function decorate(block) {
  const rows = [...block.querySelectorAll(':scope > div')];
  const getCell = (i) => rows[i]?.querySelector(':scope > div:last-child');

  // For each text field: create element, set content, move UE attributes
  const titleCell = getCell(0);
  const titleEl = document.createElement('h2');
  titleEl.textContent = titleCell?.textContent?.trim() || '';
  moveInstrumentation(titleCell, titleEl); // transfers data-aue-prop="title" etc.

  // For richtext fields: keep innerHTML, move instrumentation from cell
  const bodyCell = getCell(1);
  const bodyEl = document.createElement('div');
  bodyEl.innerHTML = bodyCell?.innerHTML || '';
  moveInstrumentation(bodyCell, bodyEl);

  // Build and replace — never discard cells before calling moveInstrumentation
  block.innerHTML = '';
  block.append(titleEl, bodyEl);
}
```

**Rule:** every call to `document.createElement` that represents a model field must
be followed by `moveInstrumentation(cell, newEl)` before appending to the DOM.
See `blocks/hero-b2b/hero-b2b.js` for a full multi-field example.

### Optimizing images

```javascript
import { createOptimizedPicture } from '../../scripts/aem.js';
import { moveInstrumentation } from '../../scripts/scripts.js';

const pic = createOptimizedPicture(img.src, img.alt, false, [{ width: '750' }]);
moveInstrumentation(img, pic.querySelector('img'));
img.closest('picture').replaceWith(pic);
```

---

## Block JSON Skeleton

```json
{
  "definitions": [{
    "title": "My Block", "id": "my-block",
    "plugins": { "xwalk": { "page": {
      "resourceType": "core/franklin/components/block/v1/block",
      "template": { "name": "My Block", "model": "my-block" }
    }}}
  }],
  "models": [{
    "id": "my-block",
    "fields": [
      { "component": "text",      "name": "title",  "label": "Title",  "valueType": "string" },
      { "component": "richtext",  "name": "text",   "label": "Body",   "valueType": "string" },
      { "component": "reference", "name": "image",  "label": "Image",  "multi": false },
      { "component": "select",    "name": "style",  "label": "Style",
        "options": [{ "name": "Default", "value": "" }, { "name": "Dark", "value": "dark" }] }
    ]
  }],
  "filters": []
}
```
