# Study Radar REST API Specification

The Study Radar API provides a RESTful interface to query research opportunities, manage sources, monitor crawl runs, test notifications, and perform manual URL ingestion.

Base URL: `http://localhost:8008/api`

---

## 1. Opportunities Endpoints

### `GET /api/opportunities/`
Returns a paginated list of research opportunities.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `country` | string | `US` or `CA` |
| `state` | string | Filter by US state name or abbreviation (e.g., `Arizona`, `AZ`) |
| `province` | string | Filter by Canadian province name or abbreviation (e.g., `Ontario`, `ON`) |
| `city` | string | Filter by city name (e.g., `Phoenix`, `Toronto`) |
| `study_type` | string | Filter by study type (e.g., `paid_survey`, `focus_group`, `user_interview`) |
| `paid` | boolean | `true` or `false` |
| `posted_within` | string | `24h`, `3d`, `7d` |
| `search` | string | Full-text search across title, description, organization, eligibility |
| `ordering` | string | `published_at`, `-published_at`, `reward_amount`, etc. |

### `GET /api/opportunities/{id}/`
Returns detailed information for a specific opportunity, including associated source sightings and geographic matches.

### `POST /api/opportunities/{id}/trigger_notification/`
Forces an immediate notification dispatch test for the specific opportunity.

---

## 2. Analytics & Metrics

### `GET /api/stats/`
Returns the core SaaS dashboard metrics (Section 59):
```json
{
  "new_24h": 12,
  "new_7d": 84,
  "us_opportunities": 65,
  "canada_opportunities": 19,
  "paid_opportunities": 70,
  "unpaid_opportunities": 14,
  "sources_monitored": 4,
  "successful_source_runs": 28,
  "failed_source_runs": 0,
  "duplicates_removed": 15,
  "total_discovered": 99,
  "server_time": "2026-10-03T12:00:00Z"
}
```

---

## 3. Manual Ingestion Tool

### `POST /api/ingest/`
Executes the inspection pipeline on a raw URL.

**Request Body:**
```json
{
  "url": "https://dsl.harvard.edu/participate",
  "save_to_database": true
}
```

**Response:**
Returns complete extraction results (classification, date, geography, 7-day freshness evaluation, qualification decision, and deduplication info).

---

## 4. Notifications

### `POST /api/notifications/test/`
Dispatches a test alert across a selected channel without requiring live external credentials.

**Request Body:**
```json
{
  "channel": "local_log"
}
```
Channels supported: `local_log`, `telegram`, `email`.

---

## 5. Sources & Runs

### `GET /api/sources/`
Lists all discovery sources.

### `POST /api/sources/{id}/toggle_active/`
Toggles source active status between enabled and disabled.

### `POST /api/sources/{id}/trigger_run/`
Triggers an immediate asynchronous crawl task for the source.

### `GET /api/sources/runs/`
Lists execution logs and metrics for source crawl runs.
