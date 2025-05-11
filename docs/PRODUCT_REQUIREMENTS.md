# Product Requirements Document — **“10-Prompt Bootstrapper”**

*v2025-05-11 (updated)*

---

## 1 Purpose

Generate **ten brand-aligned AI prompts** (plus ≤ 40-word usage tips) and a branded PDF—complete with the company’s logo and colour palette—from a single website URL, so SMBs can unlock AI value in minutes instead of days.

## 2 Problem Statement

SMBs struggle to translate their positioning into effective prompts and to package results in an on-brand format. Manual efforts are slow and inconsistent. A one-click generator that also self-brands its output removes both barriers.

## 3 Target Users & Personas

| Persona                             | Need                               | Pain                      |
| ----------------------------------- | ---------------------------------- | ------------------------- |
| **Founder / Marketer** (< 50 staff) | Instant marketing & ops prompts    | Limited bandwidth         |
| **Agency Strategist**               | Repeatable prompt packs per client | Context-switch overhead   |
| **Enablement Lead**                 | Standardised quality across teams  | Inconsistent prompt style |

## 4 Core User Flow

1. User pastes URL → clicks **Generate**.
2. **Chat Call A**
   • `web_search` pulls page HTML (≤ 4 k tokens).
   • `summarise_business` → master prompt (≤ 240 chars).
   • `fetch_brand_assets` → `{logo_url, palette}`.
3. **Chat Call B**
   • Uses master prompt + palette → drafts 3-5 prompt groups, 5 prompts each.
   • Ranks best prompt per group → writes usage tips.
4. API **streams PDF** back immediately *(MVP)*.
5. UI displays prompts & “Download PDF” link; user saves file.

*(Optional enhancement: move Chat + PDF work to a background queue; API returns `job_id`, UI polls for a signed URL.)*

## 5 Key Features

| Area                           | Requirement                                                                                                                 |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| **Input & Validation**         | Accept HTTPS URL; block localhost/private nets.                                                                             |
| **Two-Step Agent Pipeline**    | Chat A (fetch + summary + assets) and Chat B (prompt generation) for easier debug.                                          |
| **Brand-Asset Extraction**     | Parse `<meta property="og:image">` / `<link rel="icon">`; fallback to favicon APIs.                                         |
| **Palette Detection**          | Extract 3–5 dominant HEX colours with ColorThief (SVG via cairosvg).                                                        |
| **Prompt Framework Selector**  | Mix RTF, RISEN, CRISPE; ensure at least 3 domains (marketing, ops, creative).                                               |
| **Prompt Ranking**             | Score clarity & relevance; keep best per group.                                                                             |
| **Usage Guides**               | ≤ 40-word tips incl. ideal temperature/model.                                                                               |
| **PDF Exporter**               | WeasyPrint; logo top-left; palette drives cover & headings; selectable text.                                                |
| **Delivery Mode**              | **MVP:** synchronous HTTP attachment.  **Enhancement:** store PDF in object storage (e.g., S3) and return 24 h signed link. |
| **Background Jobs (Optional)** | Add Redis / RQ *or* PocketFlow async worker for >20 concurrent jobs.                                                        |
| **Dry-Run Mode**               | CLI flag returns JSON only—no PDF cost.                                                                                     |

## 6 Functional Requirements

1. **Deterministic outputs** when `seed` is fixed.
2. Prompts explicitly reference nouns/verbs from master prompt.
3. English v1; locale module pluggable.
4. PDF sent inline or via signed URL; links expire after 24 h.
5. Neutral styling fallback when no logo/palette found.

## 7 Non-Functional Requirements

| Attribute       | Target                                                                |
| --------------- | --------------------------------------------------------------------- |
| **Performance** | P95 < 25 s end-to-end (synchronous). With queue: API < 200 ms.        |
| **Cost**        | ≤ \$0.06 LLM cost per job; infra ≤ \$100 / mo (Render).               |
| **Scalability** | 20 concurrent jobs sync • 100+ with optional queue.                   |
| **Security**    | HTTPS end-to-end; OWASP input sanitisation; purge files after 7 days. |
| **Compliance**  | No long-term PII; GDPR-friendly.                                      |

## 8 Success Metrics

| KPI                                 | Target    |
| ----------------------------------- | --------- |
| Prompt-adoption (download ≤ 10 min) | ≥ 70 %    |
| Customer Effort Score (CES)         | ≥ 4.5 / 5 |
| Regeneration-rate                   | ≤ 15 %    |
| PDF / branding error-rate           | < 1 %     |

## 9 Technical Architecture

| Layer               | MVP Choice                                | Optional Enhancement                   |
| ------------------- | ----------------------------------------- | -------------------------------------- |
| **Orchestration**   | PocketFlow 0.4 Nodes                      | —                                      |
| **API**             | FastAPI (sync)                            | Same, but enqueues Redis / RQ jobs     |
| **Front-end**       | React + Vite + Tailwind (`fyne-core.css`) | —                                      |
| **Background Jobs** | —                                         | Redis / RQ or PocketFlow `run_async()` |
| **Storage**         | None (stream PDF)                         | S3/B2/etc. for signed URLs             |
| **PDF Engine**      | WeasyPrint (Cairo + Pango)                | same                                   |
| **Hosting**         | Render dynos (< \$100 / mo)               | Add Redis add-on if queue enabled      |

### 9.1 Data Flow

URL → `web_search` → HTML (≤ 4 k) → Chat A → master + assets → Chat B → prompts JSON → WeasyPrint (logo & palette) → **HTTP response (PDF)** → user.
*(With queue: PDF → object store → signed URL → front-end.)*

## 10 Assumptions

* Public site contains enough copy to infer positioning.
* Users have rights to scrape the provided URL.
* Single-language (English) in v1.

## 11 Out of Scope (v1)

* Browser extensions.
* Batch multi-URL processing.
* WYSIWYG prompt editor.

## 12 Risks & Mitigations

| Risk                             | Mitigation                                                       |
| -------------------------------- | ---------------------------------------------------------------- |
| 25 s synch time-out on big sites | Add queue + object store when concurrency or payload size grows. |
| Logo not found / monochrome      | Fallback neutral theme; allow manual logo upload.                |
| Colour extraction inaccurate     | Backup: K-means on homepage screenshot.                          |
| Model drift                      | Pin model version; nightly regression on golden sites.           |

## 13 Open Questions

1. Offer user override for logo/palette if extraction fails?
2. Map palette to Tailwind CSS custom properties for live preview?
3. Include dark-mode variant in PDF?

---

*End of PRD*
