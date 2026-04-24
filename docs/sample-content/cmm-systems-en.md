# CMM Systems Product Detail Page — Lumina Noventis
**Path:** `/en/products/cmm-systems`  
**Page title:** CMM Systems  
**SEO description:** Sub-micron coordinate measurement at production speed | SpectraLink Series | Lumina Noventis  
**Template:** Product detail (hero-b2b + section-header + cards + content-fragment)

---

## Section 1 — Hero

**Block:** `Hero B2B`

| Field | Value |
|---|---|
| Preheader | Dimensional Metrology · SpectraLink Series |
| Header (H1) | Sub-micron accuracy. Factory-floor ready. |
| Description | CMM Systems that measure to ≤ 0.05 µm uncertainty — certified for production environments from −10°C to +60°C. No cleanroom required. |
| CTA 1 | Request a Demo → `/en/contact` |
| CTA 2 | Download Datasheet → `/en/products/cmm-systems/datasheet` |
| Hero image | `/content/dam/b2b-ue/images/2-people-pc-preview.jpg` |
| Stat 1 | **≤ 0.05 µm** — Measurement Uncertainty |
| Stat 2 | **IP67** — Factory-Floor Rated |
| Stat 3 | **ISO 10360-2** — Certified Accuracy |

---

## Section 2 — Intro

**Block:** `Section Header`

| Field | Value |
|---|---|
| Eyebrow | THE SPECTRALINK CMM SYSTEM |
| Heading | Coordinate measurement built for where parts are actually made |
| Subtitle | Most CMMs live in climate-controlled measurement labs — away from your production floor, adding transport time and bottlenecks to every quality check. SpectraLink eliminates that gap. It measures directly in the production environment, delivering lab-grade results at line speed. |

---

## Section 3 — Feature-Benefit Cards

**Blocks:** `Section Header` + `Cards`

### Section Header

| Field | Value |
|---|---|
| Eyebrow | WHY ENGINEERS CHOOSE SPECTRALINK |
| Heading | Precision that keeps up with production |

### Cards (style: `feature-tile`)

**Card 1 — Measure at line speed**  
Icon: `crosshair`  
> Traditional CMMs create inspection bottlenecks. SpectraLink delivers sub-micron results in seconds — fast enough to keep pace with your production cycle, not slow it down.

**Card 2 — No cleanroom. No compromise.**  
Icon: `check-shield`  
> IP67 sealing and a −10°C to +60°C operating range mean SpectraLink works on the factory floor, not just in the lab. Measure where your parts are — not where it's convenient.

**Card 3 — Native IIoT connectivity**  
Icon: `globe`  
> OPC-UA, EtherNet/IP, and MQTT built in — not bolted on. SpectraLink connects directly to your MES, ERP, and SPC systems, feeding real-time quality data to the systems that act on it.

---

## Section 4 — Technical Specifications

**Section style:** `feature-split`  
**Blocks:** `Section Header` + `Content Fragment`

### Section Header

| Field | Value |
|---|---|
| Style | `dark-left` |
| Eyebrow | TECHNICAL SPECIFICATIONS |
| Heading | Built to the standard your tolerance requires |
| Subtitle | Every SpectraLink unit ships with a traceable calibration certificate. Measurement uncertainty is guaranteed to specification — not estimated. |
| CTA | Download Full Datasheet → `/en/products/cmm-systems/datasheet` |

### Content Fragment (ProductSpec CF)

| Field | Value |
|---|---|
| Fragment path | `/content/dam/b2b-ue/product-specs/cmm-systems` |
| Persisted query | `b2b-ue/product-spec-by-path` |
| Variable name | `path` |

**Rendered spec table data** (from the `cmm-systems` Content Fragment):

| Spec field | Value |
|---|---|
| Product Name | CMM Systems |
| Series | SpectraLink Series |
| Category | Dimensional Metrology |
| Short Description | Sub-micron coordinate measurement at production speed. Measurement uncertainty ≤ 0.05 µm without cleanroom constraints — certified for factory-floor deployment. |
| Measurement Uncertainty | ≤ 0.05 µm (ISO 10360-2) |
| Protection Rating | IP67 |
| Operating Temperature | −10°C to +60°C |
| Industrial Protocols | OPC-UA · EtherNet/IP · MQTT |
| Calibration Standard | OIML & ISO Traceable |
| Compliance | FDA 21 CFR Part 11 · EU Annex 11 |
| Report Templates | ISO/IEC 17025 compliant |
| Hero Image | `/content/dam/b2b-ue/images/2-people-pc-preview.jpg` |

> **Note:** The Content Fragment is stored at `/content/dam/b2b-ue/product-specs/cmm-systems` and uses the `ProductSpec` CF model at `/conf/b2b-ue/settings/dam/cfm/models/product-spec`. The `content-fragment` block fetches it via the `product-spec-by-path` persisted query, passing the fragment path as the `path` variable.

---

## Section 5 — Application Cards

**Blocks:** `Section Header` + `Cards`

### Section Header

| Field | Value |
|---|---|
| Eyebrow | APPLICATIONS |
| Heading | Built for where precision matters most |

### Cards (style: `solution-tile`)

**Card 1 — Aerospace**  
Icon: `crosshair` · Link: `/en/solutions/aerospace`  
> Turbine blade inspection, structural component tolerancing, and in-process airframe assembly verification — all at production rate.

**Card 2 — Medical Devices**  
Icon: `monitor` · Link: `/en/solutions/medical`  
> FDA 21 CFR Part 11 compliant measurement for implants, surgical instruments, and diagnostic equipment — with audit-ready reporting built in.

**Card 3 — Automotive**  
Icon: `hex-tolerance` · Link: `/en/solutions/automotive`  
> In-line CMM for powertrain component inspection, body panel tolerancing, and EV battery enclosure verification — integrated with your MES.

---

## Section 6 — Bottom CTA

**Block:** `Hero B2B` (variant: `centered`)

| Field | Value |
|---|---|
| Preheader | GET STARTED |
| Header | Every deployment starts with a measurement audit |
| Description | Our metrology engineers will map your tolerance requirements to the right SpectraLink configuration — and identify where in-line measurement will eliminate the most bottlenecks. |
| CTA 1 | Schedule a Call → `/en/contact` |
| CTA 2 | Download Datasheet → `/en/products/cmm-systems/datasheet` |

---

## Page Structure at a Glance

```
Section 1 — Hero B2B
  hero-b2b (image + H1 + 2 CTAs + 3 stats)

Section 2 — Intro
  section-header (eyebrow + heading + subtitle)

Section 3 — Feature Benefits
  section-header (eyebrow + heading)
  cards [feature-tile × 3] (icon + H3 + body)

Section 4 — Technical Specs        [style: feature-split]
  section-header (eyebrow + heading + subtitle + CTA)
  content-fragment → cmm-systems CF → spec table

Section 5 — Applications
  section-header (eyebrow + heading)
  cards [solution-tile × 3] (icon + H3 + body + link)

Section 6 — CTA Banner
  hero-b2b [centered] (preheader + H2 + body + 2 CTAs)
```

---

## Relationship to Other Pages

| Page | Relationship |
|---|---|
| `/en/products` | Parent listing page — links to CMM Systems via product card ("Explore CMM Systems →") |
| `/en/news/spectralink-7000` | Related article — covers the SpectraLink 7000 launch |
| `/en/solutions/aerospace` | Linked from Application card 1 |
| `/en/solutions/medical` | Linked from Application card 2 |
| `/en/solutions/automotive` | Linked from Application card 3 |
| `/content/dam/b2b-ue/product-specs/cmm-systems` | Content Fragment — supplies spec table data |
