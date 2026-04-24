# Content Fragment Folder Restructure — Language-Based DAM Paths

## Status: Structure implemented ✅

| Step | Status |
|---|---|
| `en/products/cmm-systems/.content.xml` line 103 updated to new CF path | ✅ Done by user |
| `fragment=` renamed to `reference=` in `en/products/cmm-systems/.content.xml` | ✅ Done |
| Language folder nodes created (`en` → `ar`) under `product-specs/` | ✅ Done |
| EN CF moved to `product-specs/en/cmm-systems/` (`cq:parentPath` + indexed path updated) | ✅ Done |
| Old flat `product-specs/cmm-systems/` removed from `content-source/` | ✅ Done |
| Language CF content created (ja, zh, ko, es, de, fr, ar) | ⬜ Next step |
| Non-EN products listing pages (`{lang}/products/.content.xml`) updated | ⬜ Next step |
| Non-EN cmm-systems pages (`{lang}/products/cmm-systems/.content.xml`) created | ⬜ Next step |



## Problem: Current Flat Structure Cannot Scale to Multilingual

The current DAM layout for product-spec Content Fragments is flat:

```
/content/dam/b2b-ue/product-specs/
  cmm-systems          ← single CF, EN content, no language indicator
```

This works for English only. Adding translated CFs for 7 languages into the same flat folder creates an ambiguity problem: there is no way to distinguish `cmm-systems` (EN) from `cmm-systems` (JA) without embedding the language into the node name (`cmm-systems-ja`), which does not scale and is hard to browse in the DAM UI.

---

## Decision: Language Subfolder Under `product-specs/`

```
/content/dam/b2b-ue/product-specs/
  en/
    cmm-systems          ← moved from flat root
  ja/
    cmm-systems
  zh/
    cmm-systems
  ko/
    cmm-systems
  es/
    cmm-systems
  de/
    cmm-systems
  fr/
    cmm-systems
  ar/
    cmm-systems
```

**Why this pattern:**

1. **Mirrors page content structure.** Pages live at `/content/b2b-ue/language-masters/{lang}/products/cmm-systems`. CFs at `/product-specs/{lang}/cmm-systems` follow the same language-first convention — a DAM author browsing for Japanese product content goes to `product-specs/ja/`.

2. **Standard AEM DAM convention.** Adobe's own reference implementations (WKND, We.Retail) place language-specific DAM assets under language-coded subfolders. AEM's DAM Language Copy feature also operates on this model.

3. **No GraphQL change needed.** The `product-spec-by-path` persisted query receives `path` as a variable. Each language's page XML simply passes its own language-specific path. The query itself is unchanged.

4. **Scales to future products.** Adding `optical-profilometers`, `spectrophotometers`, etc. across 8 languages is straightforward:
   ```
   product-specs/ja/optical-profilometers
   product-specs/ja/spectrophotometers
   ```
   vs. a flat folder with 40+ nodes at the root.

5. **DAM UI usability.** Authors maintaining Japanese content see only `product-specs/ja/` — not a mixed list of all languages.

---

## Why NOT the Alternative (`cmm-systems/{lang}`)

An alternative would be product-first grouping:
```
product-specs/cmm-systems/en
product-specs/cmm-systems/ja
```

This groups all language variants of one product together, but:
- The individual CF node name becomes `en`, `ja`, etc. — meaningless out of context
- Does not parallel how page content is organized
- Browsing "all Japanese CFs" requires jumping between product folders
- The CF model browser in AEM renders node names, so seeing `en`/`ja` as item names in the picker is confusing

---

## Impact Analysis

### 1. `content-source/` file system — changes required

**Delete (abandon in place):**
```
content-source/jcr_root/content/dam/b2b-ue/product-specs/cmm-systems/
```
This old path still exists on disk. It should be removed from `content-source/` so it is not re-packaged. The build will no longer include the flat `/product-specs/cmm-systems` node.

**Add:**
```
content-source/jcr_root/content/dam/b2b-ue/product-specs/en/
  .content.xml                  ← sling:OrderedFolder, title "Product Specs — EN"
  cmm-systems/
    .content.xml                ← the CF (migrated from flat root)

content-source/jcr_root/content/dam/b2b-ue/product-specs/ja/
  .content.xml                  ← sling:OrderedFolder, title "Product Specs — JA"
  cmm-systems/
    .content.xml                ← new CF with Japanese content

[repeat for zh, ko, es, de, fr, ar]
```

**`product-specs/.content.xml`** stays as-is (`sling:OrderedFolder`, title "Product Specs") — no change.

### 2. Page XML `fragment` attribute — update per language

Every `content-fragment` block in a product detail page references the CF via a `fragment=` attribute.

| Page path | Old `fragment` value | New `fragment` value | Status |
|---|---|---|---|
| `en/products/cmm-systems` | `/content/dam/b2b-ue/product-specs/cmm-systems` | `/content/dam/b2b-ue/product-specs/en/cmm-systems` | ✅ Updated by user (line 103) |
| `ja/products/cmm-systems` | _(new)_ | `/content/dam/b2b-ue/product-specs/ja/cmm-systems` |
| `zh/products/cmm-systems` | _(new)_ | `/content/dam/b2b-ue/product-specs/zh/cmm-systems` |
| `ko/products/cmm-systems` | _(new)_ | `/content/dam/b2b-ue/product-specs/ko/cmm-systems` |
| `es/products/cmm-systems` | _(new)_ | `/content/dam/b2b-ue/product-specs/es/cmm-systems` |
| `de/products/cmm-systems` | _(new)_ | `/content/dam/b2b-ue/product-specs/de/cmm-systems` |
| `fr/products/cmm-systems` | _(new)_ | `/content/dam/b2b-ue/product-specs/fr/cmm-systems` |
| `ar/products/cmm-systems` | _(new)_ | `/content/dam/b2b-ue/product-specs/ar/cmm-systems` |

### 3. GraphQL persisted query — no change

`/conf/b2b-ue/settings/graphql/persistedQueries/product-spec-by-path` takes `path` as a variable. The query body is language-agnostic. No modification required.

### 4. Build / packaging — no change

`build-packages.py` generates a site.zip filter with:
```xml
<filter root="/content/dam/b2b-ue" mode="merge"/>
```
This covers the entire `/content/dam/b2b-ue/` subtree. The new `product-specs/{lang}/` paths fall under this filter automatically. No filter changes needed.

### 5. `fragments/products/` folder — leave as-is

`/content/dam/b2b-ue/fragments/products/` is a separate empty placeholder folder unrelated to `product-specs/`. Do not move CFs there. That folder was likely intended for a different CF type (e.g. long-form editorial content fragments). Keep product-spec CFs in `product-specs/`.

---

## AEM on-author migration note

On any AEM environment where `/content/dam/b2b-ue/product-specs/cmm-systems` already exists (installed by a previous package), the old node will persist after the new package is installed — because the filter root is `/content/dam/b2b-ue` with `mode="merge"`, which adds/updates but does not delete existing nodes.

**Manual cleanup required on any environment that has the old flat CF:**
1. Open CRXDE Lite → `/content/dam/b2b-ue/product-specs/cmm-systems`
2. Delete the node
3. Reinstall the package

This is a one-time step per environment. Document it in README.

---

## File Creation Checklist

### DAM — Content Fragments

- [x] `product-specs/en/.content.xml` (folder node) ✅
- [x] `product-specs/en/cmm-systems/.content.xml` (migrated, `cq:parentPath` + indexed path updated) ✅
- [x] `product-specs/ja/.content.xml` ✅
- [ ] `product-specs/ja/cmm-systems/.content.xml`
- [x] `product-specs/zh/.content.xml` ✅
- [ ] `product-specs/zh/cmm-systems/.content.xml`
- [x] `product-specs/ko/.content.xml` ✅
- [ ] `product-specs/ko/cmm-systems/.content.xml`
- [x] `product-specs/es/.content.xml` ✅
- [ ] `product-specs/es/cmm-systems/.content.xml`
- [x] `product-specs/de/.content.xml` ✅
- [ ] `product-specs/de/cmm-systems/.content.xml`
- [x] `product-specs/fr/.content.xml` ✅
- [ ] `product-specs/fr/cmm-systems/.content.xml`
- [x] `product-specs/ar/.content.xml` ✅
- [ ] `product-specs/ar/cmm-systems/.content.xml`
- [x] Deleted `product-specs/cmm-systems/` from content-source ✅

### Page content — Products listing

- [ ] `en/products/.content.xml` — no change needed (fragment attribute not present here)
- [ ] `ja/products/.content.xml` — replace stub with full translated content
- [ ] `zh/products/.content.xml` — replace stub
- [ ] `ko/products/.content.xml` — replace stub
- [ ] `es/products/.content.xml` — replace stub
- [ ] `de/products/.content.xml` — replace stub
- [ ] `fr/products/.content.xml` — replace stub
- [ ] `ar/products/.content.xml` — replace stub

### Page content — CMM Systems detail

- [ ] `en/products/cmm-systems/.content.xml` — update `fragment` to new EN path
- [ ] `ja/products/cmm-systems/.content.xml` — create with JA content
- [ ] `zh/products/cmm-systems/.content.xml` — create
- [ ] `ko/products/cmm-systems/.content.xml` — create
- [ ] `es/products/cmm-systems/.content.xml` — create
- [ ] `de/products/cmm-systems/.content.xml` — create
- [ ] `fr/products/cmm-systems/.content.xml` — create
- [ ] `ar/products/cmm-systems/.content.xml` — create

### Total new/modified files: 32 (16 CF + 8 products pages + 8 cmm-systems pages)

---

## Translation sources

All translated copy is sourced from:

| Type | Source files |
|---|---|
| Products listing page | `docs/sample-content/translations/products-page-{lang}.md` |
| CMM Systems detail page | `docs/sample-content/translations/cmm-systems-{lang}.md` |
| CMM Systems CF fields | `docs/sample-content/translations/cmm-systems-{lang}.md` → "Rendered spec table data" section |
