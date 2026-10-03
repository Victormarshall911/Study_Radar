# Architecture & Pipeline Design

Study Radar is architected as an autonomous research opportunity discovery and aggregation platform. It decouples continuous ingestion from serving, and applies a multi-stage filtering pipeline to ensure that alerts maintain high precision.

---

## 1. Pipeline Lifecycle

```
[ Discovery / Crawler Engine ]
              │ (HTTP client / SSRF validation)
              ▼
       [ RawDocument ]
              │
              ▼
   [ Staged Classification ]
     Stage 1: Negative screening (job vacancies, sweepstakes, research papers)
     Stage 2: Deterministic pattern matching & regex heuristics
     Stage 3: AI Provider fallback (OpenAI / Compatible / Local)
              │
              ▼
   [ Intelligent Date Extractor ]
     1. JSON-LD datePublished
     2. OpenGraph / article:published_time
     3. Feed publication timestamp
     4. Text relative/exact patterns ("Posted 3 hours ago")
     * Strictly avoids deadline confusion
              │
              ▼
   [ Hybrid Geographic Resolver ]
     - Decouples researcher organization from participant location
     - Evaluates 15 decision logic cases
     - Canonical Gazetteer (All 50 US States + DC, 13 CA Provinces/Territories, Cities, Metros)
              │
              ▼
   [ 7-Day Freshness Filter ]
     - published_at >= now - 7 days
     - Discards or flags stale/uncertain candidates
              │
              ▼
   [ Multi-Level Deduplication ]
     - URL normalization (strips tracking parameters)
     - Canonical URL matching
     - Content hash matching
     - Title + Organization matching
     - Repost detection (preserves original published_at)
              │
              ▼
       [ Opportunity ]
              │
              ├──────────────────────────────────┐
              ▼                                  ▼
   [ Notification Dispatcher ]           [ REST API & Next.js ]
   - Telegram Bot API                   - Filterable feeds
   - Email (SMTP)                       - Detail drill-downs
   - Local Audit Log                    - Manual Ingestion tester
   - Duplicate alert suppression        - Source management
```

---

## 2. Component Directory Architecture
- `backend/config/`: Core Django & Celery configuration.
- `backend/apps/opportunities/`: Opportunity entity, deduplication service, and API views.
- `backend/apps/geography/`: Canonical US/Canada gazetteer, models, and 15-case geographic resolution engine.
- `backend/apps/classification/`: Staged classifier, date extraction service, and AI provider abstraction.
- `backend/apps/crawling/`: Network crawler engine, SSRF protection, HTML parsing, and manual ingestion tool.
- `backend/apps/sources/`: Source connector models, run tracking, failure logs, and discovery queries.
- `backend/apps/notifications/`: Multi-channel notification dispatcher (Telegram, Email, Local Audit Log).
- `backend/apps/analytics/`: High-level aggregated SaaS metrics (Section 59).
- `backend/apps/tasks/`: Celery asynchronous worker tasks and periodic cron beats.
- `frontend/`: Modern Next.js TypeScript + Tailwind responsive dashboard.
- `docker/`: Backend and Frontend containerization specs.
- `tests/`: End-to-end automated pytest suites (all 10 freshness + 17 geography cases).
