# Study Radar 📡

> **Autonomous Research Opportunity & Survey Discovery Platform for the United States & Canada**

Study Radar is a production-grade research opportunity aggregator that continuously discovers newly posted surveys, participant recruitment campaigns, user research interviews, focus groups, usability tests, and academic studies across the web.

It eliminates the tedious manual effort of searching job boards, universities, and social media feeds by automatically evaluating candidate opportunities, enforcing a strict **7-day freshness window**, and isolating granular **US and Canadian participant eligibility**.

---

## ⚡ The 3 Golden Rules
1. **Research Opportunity Only**: Participant recruitment only (paid/unpaid surveys, interviews, usability tests, focus groups, clinical trials). Excludes normal jobs, freelance contracts, scholarships, sweepstakes, and non-recruiting research papers.
2. **7-Day Freshness Window**: `published_at >= current_time - 7 days`. Application deadlines are **never** treated as publication dates. Unknown publication dates are never alerted.
3. **Granular US & Canada Participant Eligibility**:
   - Covers all 50 US states + DC, 13 Canadian provinces and territories, cities, regions, and nationwide scopes.
   - Decouples researcher organization location from participant location (e.g. a Michigan university study recruiting Texas residents is classified under Texas, US).

---

## 🏗️ Architecture & Pipeline
```
[Permitted Sources: RSS, APIs, Universities, Public Directories]
                           │
                           ▼
                  [CrawlEngine & HTML Parser]
                  (SSRF Protection, Sanitization)
                           │
                           ▼
                 [Staged Classifier]
        (Fast screening -> Rule-based extraction)
                           │
                           ▼
               [Intelligent Date Extractor]
          (JSON-LD -> Meta -> Patterns -> UTC)
                           │
                           ▼
              [Hybrid Geographic Resolver]
          (Canonical Gazetteer + 15 Decision Cases)
                           │
                           ▼
              [Multi-Level Deduplicator]
          (URL normalization, Content Hash, Title)
                           │
                           ▼
                  [PostgreSQL Storage]
                           │
                           ▼
                 [Notification Dispatcher]
        (Telegram, Email & Local Audit Log - No Duplicates)
                           │
                           ▼
              [Next.js Modern Web Dashboard]
```

---

## 🚀 Quickstart

### Prerequisites
- Docker & Docker Compose **OR**
- Python 3.12+ and Node.js 20+

### Option A: Running with Docker Compose (Recommended)
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Launch the entire stack
docker compose up --build -d

# 3. View logs
docker compose logs -f
```
The services will be available at:
- **Web Dashboard**: [http://localhost:3000](http://localhost:3000)
- **REST API**: [http://localhost:8008/api](http://localhost:8008/api)
- **API Health Check**: [http://localhost:8008/api/health/](http://localhost:8008/api/health/)
- **Django Admin**: [http://localhost:8008/admin/](http://localhost:8008/admin/)

*(Note: Port 8008 is mapped on the host to avoid collisions with any existing local services on port 8000).*

---

### Option B: Local Development

#### 1. Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run migrations and seed data
USE_SQLITE=True python manage.py migrate
USE_SQLITE=True python manage.py load_gazetteer
USE_SQLITE=True python manage.py seed_sources

# Start dev server on port 8008
USE_SQLITE=True python manage.py runserver 0.0.0.0:8008
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Automated Testing
Study Radar includes a comprehensive Pytest test suite covering all 10 mandatory freshness cases and all 17 mandatory geographic test cases:
```bash
USE_SQLITE=True backend/.venv/bin/pytest tests/ -v
```

---

## 📚 Documentation
- [System Architecture](docs/ARCHITECTURE.md)
- [REST API Specification](docs/API.md)
- [Data Model & Entities](docs/DATA_MODEL.md)
- [Crawler Compliance & SSRF Security](docs/CRAWLER_COMPLIANCE.md)
- [Test Strategy & Verification](docs/TESTING.md)
