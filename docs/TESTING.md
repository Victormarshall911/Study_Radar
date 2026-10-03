# Testing Guide & Verification Strategy

Study Radar contains 44 automated tests verifying the end-to-end correctness of every filtering rule, safety control, and deduplication mechanism.

---

## 1. Running the Automated Tests
Ensure your Python virtual environment is activated and run:
```bash
USE_SQLITE=True backend/.venv/bin/pytest tests/ -v
```

---

## 2. Test Suites Covered

### 1. Freshness Requirements (`tests/test_freshness.py`)
Covers the 10 mandatory freshness test cases:
1. `test_case_1_posted_1_hour_ago`: Fresh post within 1 hour is included.
2. `test_case_2_posted_1_day_ago`: Fresh post within 1 day is included.
3. `test_case_3_posted_6_days_ago`: Fresh post at 6 days is included.
4. `test_case_4_posted_exactly_7_days_ago`: Evaluates the 7-day boundary correctly.
5. `test_case_5_posted_8_days_ago`: Excludes post older than 7 days.
6. `test_case_6_posted_30_days_ago`: Excludes post older than 30 days.
7. `test_case_7_unknown_publication_date`: Never sends alert when publication date cannot be established.
8. `test_case_8_deadline_recent_but_post_is_old`: Strictly prevents deadline from being mistaken for publication date.
9. `test_case_9_repost_detection_preserves_original_date`: Reposts are recognized and original post date is preserved.
10. `test_case_10_new_recruitment_round`: Verifiable new rounds are supported.

### 2. Geographic Resolution Requirements (`tests/test_geography.py`)
Covers the 17 mandatory geographic test cases:
- US nationwide & Canadian nationwide
- Individual US states (e.g. Arizona) & Canadian provinces (e.g. Ontario)
- Individual cities (e.g. Phoenix, Toronto)
- Multi-state (California + Texas) & multi-province (Quebec + Ontario)
- Global studies with explicit US/Canada eligibility
- Foreign country exclusions (UK only, Australia only)
- Decoupling researcher location from participant eligibility (e.g. US researcher recruiting Europe participants is excluded; US university recruiting participants without US eligibility is not assumed US).
- Rejection of "remote" without participant geography.

### 3. Deduplication (`tests/test_deduplication.py`)
- URL normalization (stripping tracking query parameters like `utm_source`, `ref`, `fbclid`).
- Canonical URL multi-source consolidation under one study record.
- Content hash and normalized title matching.

### 4. Crawler SSRF Protection (`tests/test_crawler_safety.py`)
- Immediate rejection of localhost, 127.0.0.1, private CIDRs (`192.168.0.0/16`, `10.0.0.0/8`), cloud metadata IP (`169.254.169.254`), and non-HTTP schemes.

### 5. Study Classifier (`tests/test_classifier.py`)
- Positive recruitment signal recognition.
- Negative signal rejection (normal employment jobs, grant proposals, academic literature without participant recruitment).
- Reward & duration normalization.

### 6. REST API Endpoints (`tests/test_api.py`)
- Health check, Dashboard statistics, Opportunity filters, and Notification mock testing.
