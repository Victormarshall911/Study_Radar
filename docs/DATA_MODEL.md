# Database Architecture & Entity Relationships

The Study Radar data layer is built on PostgreSQL using Django ORM with full UUID primary keys, normalized relationships, and strategic indexing for sub-second queries.

---

## 1. Core Entities

### `Opportunity`
The central canonical research study record.
- `id`: UUID (Primary Key)
- `title`: Extracted title string
- `normalized_title`: Cleaned lowercase alphanumeric title for deduplication
- `study_type`: `paid_survey`, `focus_group`, `user_interview`, `usability_test`, etc.
- `source_url`: URL where the study was first observed
- `canonical_url`: Normalized canonical URL (stripped of UTM parameters)
- `published_at`: Canonical UTC timestamp
- `published_date_precision`: `exact_datetime`, `exact_date`, `relative_datetime`, `relative_date`, `approximate`, `unknown`
- `date_confidence`: Float (0.0 to 1.0)
- `repost_detected`: Boolean indicating if a newer post duplicates an older study
- `reward_amount`: Decimal (e.g. 50.00)
- `reward_currency`: ISO currency code (`USD`, `CAD`)
- `reward_text`: Raw string (e.g. "$50 Amazon gift card")
- `is_paid`: Boolean
- `duration_minutes`: Integer (e.g. 30)
- `eligibility_text`: Summary of participant criteria
- `geography_status`: `us_eligible`, `ca_eligible`, `us_ca_eligible`, `outside_target`, `unknown`
- `participant_geo_confidence`: Float (0.0 to 1.0)
- `status`: `discovered`, `processing`, `verified`, `eligible`, `excluded`, `duplicate`, `expired`
- `has_been_notified`: Boolean
- `notification_count`: Integer
- `content_hash`: SHA256 of cleaned document text

### `OpportunitySource`
Associates multiple discovery origins with a single canonical Opportunity record.
- `opportunity`: ForeignKey -> `Opportunity`
- `source`: ForeignKey -> `Source`
- `source_url`: URL string
- `raw_document`: ForeignKey -> `RawDocument`

### `Geography`
Canonical gazetteer entries for countries, states, provinces, territories, cities, and regions.
- `country`: `US` or `CA`
- `state_province`: Name string (e.g. `Arizona`, `Ontario`)
- `state_code`: Code string (`AZ`, `ON`)
- `city`: City name (`Phoenix`, `Toronto`)
- `scope`: `nationwide`, `state`, `province`, `city`, `metro_area`, `remote`
- `is_us`, `is_ca`: Booleans
- `aliases`: JSON list of variations and keywords

### `OpportunityGeography`
Many-to-Many junction linking an `Opportunity` to matched `Geography` entities.
- `opportunity`: ForeignKey -> `Opportunity`
- `geography`: ForeignKey -> `Geography`
- `scope`: Geographic scope for this specific link
- `confidence`: Confidence score

### `Notification` & `NotificationDelivery`
Tracks alert events and per-channel delivery attempts.
- `notification`: Links to `Opportunity` and `AlertRule`
- `deliveries`: Child records for each channel (`telegram`, `email`, `local_log`)
- Stores delivery status, errors, response payloads, and timestamps.
