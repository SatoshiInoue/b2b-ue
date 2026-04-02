# b2b-ue — B2B Theme Starter for AEM EDS + Universal Editor

A production-quality B2B website starter kit for Adobe Experience Manager Edge Delivery Services (EDS) + Universal Editor (XWalk). Ships as a standalone site for the fictional company **Lumina Noventis** (precision optics and measurement instruments).

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Node.js | 18+ | `npm run build:json`, linting |
| Python | 3.8+ | `build-packages.py` — AEM content package builder |
| AEM Cloud | CS 2024+ | Author instance + Universal Editor |
| AEM EDS | — | Content delivery via `main--b2b-ue--{org}.aem.page` |

---

## Quick Start

```bash
git clone https://github.com/SatoshiInoue/b2b-ue.git
cd b2b-ue
npm install
```

---

## Key Commands

```bash
# After editing any _*.json source file (block models, filters):
npm run build:json

# After updating content-package/ or site.zip:
npm run build:packages          # both packages
npm run build:packages:template # template-only package
npm run build:packages:site     # full-install package

# Lint JS + CSS:
npm run lint
```

---

## Content Package Build Process

### Overview

The content package system has two outputs, both generated from `content-package/` as the single source of truth:

| File | Use case |
|---|---|
| `b2b-ue-template-1.0.0.zip` | New environment setup — install, then create the site via Quick Site Creation wizard |
| `b2b-ue-site-1.0.0.zip` | Dev iteration — reinstall at any time to push page content updates |

### Source of truth: `content-package/`

```
content-package/
  jcr_root/conf/global/site-templates/b2b-ue-1.0.0/
    .content.xml          ← template metadata
    site.zip              ← inner package: page content, DAM, CF models
    previews/             ← thumbnail for Quick Site Creation UI
  META-INF/vault/
    config.xml            ← Vault config (shared by both outputs)
    filter.xml            ← used only for template package
    properties.xml        ← used only for template package
```

**Never edit the output ZIPs directly.** Edit sources in `content-package/` and regenerate.

### Rebuilding `site.zip` (inner package)

`site.zip` contains the actual page content (`/content/b2b-ue/`), DAM assets (`/content/dam/b2b-ue/`), and site configuration (`/conf/b2b-ue/`). It is rebuilt via Python scripts when page content changes:

```bash
python3 /path/to/rebuild_site_zip.py   # rebuilds content-package/.../site.zip
npm run build:packages                  # regenerates both outer ZIPs
```

> **Note:** The rebuild scripts are separate from this repo (stored locally). If you need to update page content — adding blocks, editing homepage structure — edit the XML in the rebuild script, run it, then run `npm run build:packages`.

### Generating output packages

```bash
npm run build:packages
```

This runs `build-packages.py`, which:

1. **`b2b-ue-template-1.0.0.zip`** — installs the Quick Site Creation template. The embedded `site.zip` is rebuilt at package-build time with CF model nodes removed (prevents a `dam:AssetModel` rollback that would otherwise leave the site empty after QSC).
2. **`b2b-ue-site-1.0.0.zip`** — installs the template + expanded page content + DAM. Used for bulk content updates after the site exists. Uses:
   - `mode="replace"` for the template path and DAM
   - **merge** for `/content/b2b-ue` — preserves site-level properties written by Quick Site Creation
   - **`/conf/b2b-ue` is entirely excluded** — this path is owned by Quick Site Creation. It stores the `franklin.delivery` GitHub proxy config that lets AEM Author serve `component-models.json`, `component-filters.json`, and `component-definition.json` to Universal Editor. Overwriting it causes 404s on component JSON.

### Two-approach workflow

**Approach 1 — Template → Quick Site Creation (recommended for new environments):**
1. Go to CRX Package Manager (`/crx/packmgr`)
2. Upload and install `b2b-ue-template-1.0.0.zip`
3. **Pre-flight check:** If `/content/dam/b2b-ue` exists from a previous install, delete it via CRXDE Lite before continuing. An existing DAM tree causes `site.zip` to roll back during QSC, leaving no site.
4. Go to AEM Sites console → **Create → Site from Template**
5. Select **B2B UE Starter** → fill in title → Create
6. AEM installs the embedded `site.zip` — the site is created at `/content/b2b-ue/` with all blocks pre-configured (hero-b2b, solutions grid, etc.)
7. This also writes the `franklin.delivery` proxy config to `/conf/b2b-ue`, which Universal Editor needs to load component models

**Approach 2 — Content package (dev iteration / bulk updates / standalone install):**
1. Go to CRX Package Manager → upload and install `b2b-ue-site-1.0.0.zip`
2. Reinstall at any time to push page content and DAM updates
3. **Can also create the site on a fresh instance** (skips the QSC wizard) — but Universal Editor will not have component models until `/conf/b2b-ue` exists. Run Approach 1 at least once per environment to set up the conf, then use Approach 2 for all subsequent updates.

> **Recovery from broken styles / component-*.json 404:** If `/conf/b2b-ue` was accidentally overwritten, delete `/conf/b2b-ue` via CRXDE Lite and delete the site, then repeat Approach 1 to restore the proxy configuration.

---

## Frontend Development

Blocks live in `blocks/`. Each block has three files:

```
blocks/{name}/
  {name}.js          ← decorator: export default function decorate(block) {}
  {name}.css         ← styles
  _{name}.json       ← UE model definitions (definitions + models + filters)
```

After editing any `_*.json` file:
```bash
npm run build:json
```

This merges all source JSON files into the root `component-*.json` files that AEM reads. **Never edit the root `component-*.json` directly.**

### Block inventory

| Block | Description |
|---|---|
| `header` | Dynamic navigation — fetches `/{lang}/nav` fragment |
| `footer` | Static footer — fetches `/{lang}/footer` fragment |
| `fragment` | Required by header + footer for `loadFragment()` |
| `hero-b2b` | Full-width hero with preheader, headline, dual CTAs, trust stats |
| `section-header` | Eyebrow + heading + subtitle with gold decorative lines |
| `cards` + `card` | Card grid — supports `solution-tile` style with SVG icon field |
| `cta-link` | Centered text link with gold underline |
| `list` | Dynamic page list with Card/Small/Medium styles, pagination |
| `solutions-grid` | 6-tile solution area grid |
| `spec-table` | Key-value specification table with RTL support |

---

## Multi-Language

8 languages: `en`, `ja`, `zh`, `ko`, `es`, `de`, `fr`, `ar` (Arabic/RTL)

Arabic RTL is handled via `[dir="rtl"]` CSS scopes. The `ar` path sets `document.documentElement.dir = 'rtl'` in `scripts.js`.

---

## Design Reference

Design mockups (desktop 1440px + mobile 390px) are documented in:
- `docs/design/design-summary.md` — English
- `docs/design/design-summary-ja.md` — Japanese

Brand colors:

| Token | Value |
|---|---|
| Primary | `#003087` Deep navy |
| Secondary | `#0066cc` Mid blue (interactive/hover) |
| Accent | `#e8b400` Gold (CTAs, highlights) |
| Dark BG | `#001840` Footer/dark sections |
| Surface | `#f5f7fa` Light section backgrounds |

---

## Repository

- **GitHub:** `SatoshiInoue/b2b-ue`
- **AEM Author:** `author-p161901-e1740392.adobeaemcloud.com`
- **EDS delivery:** `main--b2b-ue--SatoshiInoue.aem.page`
- **Content path:** `/content/b2b-ue/us/{lang}/`
- **DAM path:** `/content/dam/b2b-ue/`
