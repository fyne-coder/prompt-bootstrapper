# Product Requirements Document — **“10-Prompt Bootstrapper”**

*v2025-05-11 – updated: OpenAI **web** tool → BeautifulSoup fallback; still PocketFlow, no S3*

---

## 1 Purpose

Generate **ten brand-aligned AI prompts** (each with a ≤ 40-word “When to use” tip) and a branded PDF—logo, colours, selectable text—from a single website URL, so SMBs unlock AI value in minutes.

## 2 Problem Statement

SMBs waste time converting their messaging into effective AI prompts and packaging them in an on-brand format. A one-click generator that also self-brands its output removes both barriers.

## 3 Target Users & Personas

| Persona (<50 staff)    | Need                               | Pain                      |
| ---------------------- | ---------------------------------- | ------------------------- |
| **Founder / Marketer** | Instant marketing & ops prompts    | Limited bandwidth         |
| **Agency Strategist**  | Repeatable prompt packs per client | Context-switch overhead   |
| **Enablement Lead**    | Standardised quality across teams  | Inconsistent prompt style |

## 4 Core User Flow

1. User pastes URL → clicks **Generate**.

2. **PocketFlow DAG** runs synchronously:

   | Step | Node (simplified)                                           | Output / Notes                          |
   | ---- | ----------------------------------------------------------- | --------------------------------------- |
   | 1    | **`WebFetchNode`** (OpenAI `web.search_query` → `web.open`) | Raw HTML *(homepage + depth-1)*         |
   | 1a   | *(fallback)* `LocalFetchNode` (`requests` + BeautifulSoup)  | Raw HTML if tool fails or < 500 chars   |
   | 2    | `CleanNode`                                                 | Text sans boilerplate                   |
   | 3    | `KeyphraseNode`                                             | 15 + key phrases                        |
   | 4    | `FrameworkSelectNode`                                       | Framework plan (RTF, RISEN, CRISPE mix) |
   | 5    | `PromptDraftNode`                                           | 15–25 raw prompts                       |
   | 6    | `DeduplicateNode`                                           | Unique prompts                          |
   | 7    | `BusinessAnchorGuard`                                       | Filter prompts missing scraped nouns    |
   | 8    | `QuotaEnforceNode`                                          | Slice/raise until **exactly 10**        |
   | 9    | `ExplanationNode`                                           | ≤ 40-word tips                          |
   | 10   | `PdfBuilderNode`                                            | Branded PDF                             |
   | 11   | `SaveArtifactNode`                                          | `/exports/{job_id}.pdf` (local)         |

3. API streams PDF response; front-end shows prompts + **Download** button (inline Blob).

4. **Optional async mode:** `/generate` returns `job_id`; front-end polls `/status`, then fetches `/download/{job_id}` (serves file from local disk, TTL = 24 h).

## 5 Key Features

| Area                         | Requirement                                                                                                                                                                                          |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Input & Validation**       | HTTPS URL; primary fetch via *OpenAI web tool* (`search_query` → `open`). If tool errors or returns < 500 chars, fall back to `requests` + BeautifulSoup. Block private networks.                    |
| **PocketFlow Prompt Engine** | Nodes listed in §4. Framework quota: 3 Marketing, 2 Sales, 2 Success, 2 Product, 1 Ops. Each prompt ≤ 220 tokens, imperative verb, cites scraped noun, deterministic seed = SHA-256(URL + model ID). |
| **Quality Filters**          | `DeduplicateNode` (≥ 85 % cosine), `BusinessAnchorGuard`, toxicity < 0.3.                                                                                                                            |
| **PDF Exporter**             | WeasyPrint; one prompt per page; TOC 1-10; logo top-left if favicon < 100 kB; palette colours on cover & headings; selectable text.                                                                  |
| **Delivery Mode**            | **Sync PDF stream (MVP)**. **Async enhancement:** serve `/exports/*` file; no object storage.                                                                                                        |
| **Background Jobs (opt.)**   | PocketFlow `run_async()` + Redis/RQ for > 20 concurrent jobs.                                                                                                                                        |
| **Dry-Run Mode**             | CLI flag returns JSON only (skip PDF).                                                                                                                                                               |

## 6 Functional Requirements

1. **F1 Prompt Quota** — DAG aborts if final list ≠ 10.
2. **F2 Category Compliance** — 3-2-2-2-1 mix enforced.
3. **F3 Business Anchoring** — every prompt contains a scraped brand/entity term.
4. **F4 Determinism** — fixed seed → byte-identical prompt JSON.
5. **F5 Fallback Flow** — if copy < 500 chars, request user paste or LinkedIn scrape before continuing.
6. **F6 PDF Delivery** — stream inline; in async mode, `/download/{id}` link valid 24 h; local purge after 7 days.

## 7 Non-Functional Requirements

| Attribute       | Target                                                             |
| --------------- | ------------------------------------------------------------------ |
| **Performance** | P95 < 25 s sync; async API < 200 ms.                               |
| **Cost**        | ≤ \$0.06 LLM/job; infra ≤ \$100/mo.                                |
| **Scalability** | 20 concurrent sync • 100+ async with Redis.                        |
| **Security**    | HTTPS, OWASP sanitisation, files outside web-root, auto-purge 7 d. |
| **Compliance**  | GDPR-friendly (user delete endpoint).                              |

## 8 Success Metrics

| KPI                      | Target  |
| ------------------------ | ------- |
| Prompt download ≤ 10 min | ≥ 70 %  |
| CES                      | ≥ 4.5/5 |
| Regeneration rate        | ≤ 15 %  |
| PDF/branding error rate  | < 1 %   |

## 9 Technical Architecture

| Layer             | MVP Choice                                                               | Optional Enhancement        |
| ----------------- | ------------------------------------------------------------------------ | --------------------------- |
| **Orchestration** | PocketFlow 0.4 DAG                                                       | PocketFlow async + Redis    |
| **API**           | FastAPI (sync)                                                           | Queue endpoints             |
| **Front-end**     | React + Vite + Tailwind (`fyne-core.css`)                                | —                           |
| **Scraper**       | **OpenAI web tool** in `WebFetchNode`; fallback `requests`+BeautifulSoup | Add Playwright for heavy JS |
| **Storage**       | Local `/exports` dir                                                     | —                           |
| **PDF Engine**    | WeasyPrint                                                               | —                           |
| **Hosting**       | Render Standard dyno (< \$100/mo)                                        | Add Redis add-on            |

### 9.1 Data Flow

URL → `WebFetchNode` (or fallback) → `CleanNode` → … → `PdfBuilderNode` → `/exports/{id}.pdf` → streamed HTTP *(sync)*
*(Async: front-end polls; `/download/{id}` reads local file).*

## 10 Assumptions

* Public site provides copy or user furnishes it.
* User owns rights to scrape URL.
* English-only v1.

## 11 Out of Scope (v1)

* Browser extensions.
* Batch multi-URL.
* WYSIWYG prompt editor.

## 12 Risks & Mitigations

| Risk                                    | Mitigation                                                        |
| --------------------------------------- | ----------------------------------------------------------------- |
| **OpenAI web tool rate-limit / outage** | Automatic fallback to local fetch; monitor `fetch_fallback_rate`. |
| Local disk fills                        | `SaveArtifactNode` checks `MAX_DISK_GB`, cron purge > 7 d.        |
| Logo not found / monochrome             | Neutral theme; optional manual logo upload.                       |
| Colour extraction inaccurate            | Fallback: K-means on homepage screenshot.                         |
| Model drift                             | Pin model ver.; nightly regression on golden sites.               |

## 13 Open Questions

1. Allow user-supplied logo/palette if extraction fails?
2. Surface JSON + PDF side-by-side in UI for advanced users?
3. Offer dark-mode PDF variant?

---

*End of PRD*
