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

## 4 Core Use-Flow

1. User enters URL → **Validate & crawl** (homepage + first-level links, respect robots).
2. **Extract copy** → title, meta-description, visible H1-H3, JSON-LD product blocks.
   • If < 500 chars of usable text ⇒ ask user for extra copy or pull LinkedIn “About”.
3. **LLM engine** generates **exactly 10 prompts** using category quota + frameworks (see §5).
4. Prompts + 30-word “When to use” tips returned → one-click **PDF export**.
5. Job & artefacts stored 7 days, then auto-purged.

## 5 Key Features

| Area                           | Requirement                                                                                                                 |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| **Web Scraper**          | Crawl depth = 1; throttle; fail when copy < 500 chars & no fallback provided.                                                                                                                                             |
| **Content Parser**       | Strip boilerplate; output list of key-phrases (≥ 15) for relevance scoring.                                                                                                                                               |
| **LLM Prompt-Generator** | Always output **10 prompts** with this mix → 3 Marketing, 2 Sales, 2 Success, 2 Product, 1 Ops. Each starts with an imperative verb, cites ≥ 1 scraped noun, includes output constraints & named framework, ≤ 220 tokens. |
| **Explanation Writer**   | ≤ 30 words “When to use” note appended to each prompt.                                                                                                                                                                    |
| **Quality Filters**      | Reject prompts lacking business nouns, duplicates (> 85 % similarity) or toxicity score > 0.3.                                                                                                                            |
| **PDF Exporter**         | One prompt per page; selectable text only; TOC lists 1-10. Embed favicon if < 100 kB.                                                                                                                                     |
| **Audit Log**            | Store scrape payload, prompt JSON, and seed-hash for determinism (URL + model ID).                                                                                                                                        |

## 6 Functional Requirements

* **F1 Prompt Quota** Exactly 10 prompts per job or API returns 422.
* **F2 Category Compliance** Prompt set must satisfy the 3-2-2-2-1 quota.
* **F3 Business Anchoring** Every prompt contains a scraped brand/entity term.
* **F4 Determinism** Same URL + model version = byte-identical prompt JSON.
* **F5 Fallback Flow** If usable copy < 500 chars, system pauses and requests extra input before continuing.
* **F6 PDF Integrity** Unit test verifies 10 prompt titles rendered; job fails otherwise.

## 7 Non-Functional Requirements

| Attribute       | Target                                                                |
| --------------- | --------------------------------------------------------------------- |
| **Performance** | P95 < 25 s end-to-end (synchronous). With queue: API < 200 ms.        |
| **Cost**        | ≤ \$0.06 LLM cost per job; infra ≤ \$100 / mo (Render).               |
| **Scalability** | 20 concurrent jobs sync • 100+ with optional queue.                   |
| **Security**    | HTTPS end-to-end; OWASP input sanitisation; purge files after 7 days. |
| **Compliance**  | No long-term PII; GDPR-friendly.                                      |
| **Security NF5** | Block private-network URLs; sanitize HTML before LLM.                |
| **Compliance NF6** | GDPR: user may delete artefacts instantly via API.                 |

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
* **Scraper Service** → Playwright + Readability, BeautifulSoup fallback.
* **Prompt Engine** → LangChain router picks framework, ranks prompts by cosine relevance × verb diversity; keeps top 10.
* **PDF Service** → WeasyPrint template with Jinja loop (`for p,t in zip(prompts,tips)`).

### 9.1 Data Flow

URL → Scraper → Clean HTML (≥ 500 chars) → Key-phrases JSON → LLM (seeded) → **10-prompt JSON** → PDF Builder → S3 → Signed URL → User.

## 10 Assumptions

* Site owner has rights to be scraped **and** will supply extra copy if needed.

## 11 Out of Scope (v1)

* Editable prompt WYSIWYG.
* Batch processing.
* Real-time Chrome extension.

## 12 Risks & Mitigations

| Risk                             | Mitigation                                          |
| -------------------------------- | --------------------------------------------------- |
| Low-content sites block progress | Fallback flow requiring user copy / LinkedIn scrape |
| Framework mix feels off per user | Future setting to weight categories, not v1         |

## 13 Open Questions

1. Offer user override for logo/palette if extraction fails?
2. Map palette to Tailwind CSS custom properties for live preview?
3. Include dark-mode variant in PDF?

---

## 14 Validation Tests (CI)

1. **Unit** — `example.com` fixture → assert 10 prompts JSON & 10 `<h2>` in PDF.
2. **Smoke** — URL with 300-char copy triggers fallback prompt.
3. **Regression** — When site text unchanged, prompt set Levenshtein distance ≤ 10 %.

*End of PRD*
