# BUILD: STUDY RADAR

You are an autonomous senior full-stack engineer, backend engineer, data engineer, and product architect.

I want you to build a production-quality web application called **Study Radar**.

The purpose of Study Radar is to continuously discover **new research studies, surveys, participant recruitment opportunities, user research, focus groups, interviews, usability tests, academic studies, consumer research, and similar research-participation opportunities** from permitted public sources across the web.

The application is NOT a profile-matching platform.

The central requirement is:

> Find research opportunities intended for participants in the United States or Canada, and alert me only when the opportunity was posted within the last 7 days.

The system must recognize nationwide opportunities as well as opportunities restricted to specific states, provinces, territories, regions, cities, or combinations of locations.

Do not build this as a simple scraper. Build it as a modular **research-opportunity discovery and aggregation platform**.

---

# 1. CORE PRODUCT REQUIREMENTS

Every discovered opportunity must pass the following conceptual pipeline:

SOURCE DISCOVERY
→ CONTENT EXTRACTION
→ STUDY CLASSIFICATION
→ POST DATE EXTRACTION
→ GEOGRAPHIC ELIGIBILITY EXTRACTION
→ 7-DAY FRESHNESS FILTER
→ DEDUPLICATION
→ DATA NORMALIZATION
→ DATABASE
→ NOTIFICATION
→ WEB DASHBOARD

The system must continuously discover opportunities rather than relying on me manually searching websites.

The user should be able to open the dashboard and immediately see recently discovered opportunities.

---

# 2. ABSOLUTE FILTERING RULES

These are mandatory.

## Rule A — Research opportunity only

Include things such as:

* Paid surveys
* Unpaid surveys
* Academic surveys
* Market research
* Consumer research
* Research studies
* Participant recruitment
* Focus groups
* User interviews
* UX research
* Usability testing
* Product research
* Diary studies
* Remote research studies
* In-person research studies
* University research
* Behavioral research
* Technology research
* Software/product research
* General participant studies

Exclude:

* Normal job vacancies
* Freelance jobs
* Scholarships
* Grants
* Competitions
* Sweepstakes
* News articles
* General blog posts
* Marketing articles
* Generic advertisements
* Research papers that are not recruiting participants
* Academic papers with no participant recruitment opportunity

The classifier must determine whether something is actually an opportunity for a person to participate.

---

# 3. 7-DAY FRESHNESS REQUIREMENT

This is one of the most important features.

Only opportunities posted within the last 7 days are eligible for an alert.

Use the actual publication/post date whenever possible.

Conceptually:

published_at >= current_time - 7 days

Do NOT use the deadline as a substitute for the publication date.

Example:

A study was posted 20 days ago but closes in 2 days.

Result:

DO NOT ALERT.

A study was posted yesterday and closes in 30 days.

Result:

ALERT.

A study was posted 6 days ago and closes tomorrow.

Result:

ALERT.

A study was posted 8 days ago.

Result:

DO NOT ALERT.

---

# 4. POST DATE EXTRACTION

The system must be intelligent about dates.

Try date sources in approximately this order:

1. Explicit published/posted date on the page
2. Structured metadata
3. JSON-LD
4. OpenGraph/meta information
5. RSS publication date
6. Official API timestamp
7. Page-specific timestamp
8. Search/discovery metadata as a lower-confidence fallback

Recognize dates such as:

* October 2, 2026
* 2 Oct 2026
* 2026-10-02
* Yesterday
* 3 hours ago
* 5 days ago
* Posted Monday
* Published 2d ago

Normalize all dates into a canonical UTC datetime while preserving the source timezone when available.

Store:

* published_at
* published_at_timezone
* published_date_precision
* date_source
* date_confidence

Possible precision values:

* exact_datetime
* exact_date
* relative_datetime
* relative_date
* approximate
* unknown

If the system cannot establish a reasonably reliable publication date, do NOT send an alert.

Do not confuse:

* Published date
* Updated date
* Application deadline
* Event date
* Study start date
* Study end date

with one another.

Prefer the original publication/recruitment date.

If a page only exposes an update date and there is no evidence of when recruitment was originally posted, flag the date as uncertain and do not treat it as a fresh opportunity unless the evidence is sufficient.

---

# 5. GEOGRAPHIC FILTER — UNITED STATES AND CANADA

This is the second most important feature.

The system must find opportunities intended for participants anywhere in:

## United States

Recognize all 50 states and Washington, DC.

Include:

Alabama
Alaska
Arizona
Arkansas
California
Colorado
Connecticut
Delaware
Florida
Georgia
Hawaii
Idaho
Illinois
Indiana
Iowa
Kansas
Kentucky
Louisiana
Maine
Maryland
Massachusetts
Michigan
Minnesota
Mississippi
Missouri
Montana
Nebraska
Nevada
New Hampshire
New Jersey
New Mexico
New York
North Carolina
North Dakota
Ohio
Oklahoma
Oregon
Pennsylvania
Rhode Island
South Carolina
South Dakota
Tennessee
Texas
Utah
Vermont
Virginia
Washington
West Virginia
Wisconsin
Wyoming
District of Columbia

Support state abbreviations such as:

CA
TX
NY
AZ
FL
WA
etc.

## Canada

Recognize all provinces and territories:

Alberta
British Columbia
Manitoba
New Brunswick
Newfoundland and Labrador
Nova Scotia
Ontario
Prince Edward Island
Quebec
Saskatchewan
Northwest Territories
Nunavut
Yukon

Support abbreviations such as:

ON
QC
BC
AB
MB
SK
NS
NB
PE
NL
YT
NT
NU

---

# 6. GEOGRAPHIC TARGETING MUST BE GRANULAR

Do not only detect country.

The system must understand opportunities such as:

"Looking for Arizona residents"

"Participants needed in Phoenix"

"California residents wanted"

"People living in Southern California"

"Adults across the United States"

"US residents only"

"Residents of Ontario"

"Toronto residents"

"Participants from Vancouver"

"Canadian residents"

"People in Quebec and Ontario"

"Participants from Texas, Florida and New York"

"Residents of the Northeast United States"

"Adults living anywhere in Canada"

"Residents of the United States and Canada"

"People in the Greater Toronto Area"

"Phoenix metro area residents"

"Participants in Los Angeles County"

All of these should be normalized into structured geographic information.

---

# 7. VERY IMPORTANT: DISTINGUISH PARTICIPANT LOCATION FROM ORGANIZATION LOCATION

The system must NOT make this mistake:

Example:

A university in Michigan publishes a study.

The page says:

"Looking for people living in Texas."

The opportunity belongs to:

Texas / United States

NOT Michigan.

Likewise:

A Canadian company publishes a study seeking California residents.

That belongs to:

California / United States.

The researcher/company/university location is NOT automatically the participant location.

The system must extract:

* participant geography
* study location
* researcher/company location

as separate concepts.

Participant eligibility is what controls the geographic filter.

---

# 8. GEOGRAPHIC SCOPE

Create structured geographic scope values such as:

* country
* state
* province
* territory
* region
* city
* county
* metropolitan_area
* postal_area
* nationwide
* multi_state
* multi_province
* remote
* unknown

Examples:

US nationwide:

{
"country": "US",
"scope": "nationwide"
}

Arizona:

{
"country": "US",
"state": "Arizona",
"scope": "state"
}

Phoenix:

{
"country": "US",
"state": "Arizona",
"city": "Phoenix",
"scope": "city"
}

Ontario:

{
"country": "CA",
"province": "Ontario",
"scope": "province"
}

Toronto:

{
"country": "CA",
"province": "Ontario",
"city": "Toronto",
"scope": "city"
}

---

# 9. GEOGRAPHIC CLASSIFICATION SHOULD BE HYBRID

Do not depend entirely on an LLM.

Use a combination of:

1. A normalized geographic database/gazetteer
2. Deterministic pattern matching
3. State/province abbreviation detection
4. City/region matching
5. NLP/LLM extraction as fallback
6. Confidence scoring

Maintain a canonical geography dataset for:

* countries
* US states
* US state abbreviations
* Canadian provinces
* Canadian province abbreviations
* territories
* major cities
* counties
* major metropolitan areas
* common regional names

Build this so it can be expanded later.

---

# 10. IMPORTANT GEOGRAPHIC DECISION LOGIC

Include an opportunity when:

### Case 1

It explicitly targets the United States.

INCLUDE.

### Case 2

It explicitly targets Canada.

INCLUDE.

### Case 3

It targets an individual US state.

INCLUDE.

### Case 4

It targets an individual Canadian province or territory.

INCLUDE.

### Case 5

It targets a US city/region.

INCLUDE if that location is in the US.

### Case 6

It targets a Canadian city/region.

INCLUDE if that location is in Canada.

### Case 7

It targets multiple US states.

INCLUDE.

### Case 8

It targets multiple Canadian provinces/territories.

INCLUDE.

### Case 9

It targets both US and Canada.

INCLUDE.

### Case 10

It says "North America" and explicitly includes US/Canada participation.

INCLUDE.

### Case 11

It is worldwide/global and explicitly allows US and/or Canadian residents.

INCLUDE.

### Case 12

It only says "remote" without identifying participant geography.

DO NOT assume US/Canada.

Require enough evidence that US/Canada residents are eligible.

### Case 13

The only US/Canada location is the researcher/company/university location.

DO NOT assume participant eligibility.

### Case 14

It is strictly restricted to a country outside US/Canada.

EXCLUDE.

### Case 15

Geographic eligibility is unknown.

Store it if useful for later review, but DO NOT alert.

---

# 11. DEDUPLICATION

The same opportunity can appear on multiple websites.

For example:

* Reddit
* University website
* Research platform
* Search result
* Forum
* Linked page
* Company website

The system must detect duplicates.

Implement multi-level deduplication.

Use:

1. Canonical URL
2. Normalized URL
3. Content hash
4. Normalized title
5. Research organization
6. Study identifier
7. Semantic similarity where appropriate

Create a canonical opportunity record and store multiple source references under it.

Example:

ONE STUDY

Sources:

* Source A
* Source B
* Source C

The user should receive one notification, not three.

---

# 12. REPOSTING AND OLD STUDIES

Be careful with reposted studies.

Example:

Original post:

September 1

Then another website republishes the same study on October 2.

Do not blindly treat the old opportunity as new.

Attempt to detect the original publication date.

If it is only an old study being copied elsewhere, do not alert it as a new October opportunity.

However, if the study has genuinely opened a new recruitment round or has a new participant recruitment posting, allow it to be treated as a new opportunity where there is evidence supporting that.

Store:

* original_published_at
* discovered_at
* last_seen_at
* repost_detected
* recruitment_round
* canonical_opportunity_id

---

# 13. SOURCE ARCHITECTURE

Do NOT create one giant scraper.

Create a modular source adapter architecture.

Example:

sources/
base/
search/
rss/
api/
website/
reddit/
university/
research_platform/
forum/
custom/

Every connector should implement a standard interface similar to:

discover()
fetch()
parse()
normalize()
return candidates

Each source should output a common internal format regardless of origin.

Example:

StudyCandidate:

{
title,
source_name,
source_url,
canonical_url,
raw_content,
published_at,
date_confidence,
participant_geography,
study_type,
reward,
duration,
eligibility_text,
application_url
}

---

# 14. SCRAPING AND SOURCE COMPLIANCE

This is extremely important.

Use public pages, official APIs, RSS feeds, sitemaps, permitted crawling, and other authorized access methods.

Before implementing a source connector:

* inspect the site's current public rules
* inspect API documentation if available
* inspect robots.txt where applicable
* respect terms and access restrictions
* respect rate limits
* implement reasonable delays
* identify the crawler with a sensible user agent
* cache requests
* avoid unnecessary requests

Do NOT:

* bypass CAPTCHAs
* bypass authentication
* bypass paywalls
* evade anti-bot systems
* circumvent access controls
* create fake accounts to scrape content
* use stolen credentials
* bypass technical restrictions
* intentionally overload websites

If a source cannot legally/technically be accessed, create an adapter abstraction for it but keep that connector disabled rather than attempting to circumvent the restriction.

The system must be source-agnostic so that compliant data sources can be added later.

---

# 15. SOURCE DISCOVERY

The discovery engine should support multiple mechanisms.

Build abstractions for:

* direct website crawling
* RSS feeds
* sitemaps
* public APIs
* search/index providers
* public research directories
* university research pages
* public recruitment pages
* publicly accessible communities where automated access is permitted

Use configurable discovery queries based on combinations of terms such as:

"paid survey"
"research study participants"
"participants needed"
"research participants"
"take part in research"
"paid research"
"focus group"
"user research"
"usability study"
"consumer research"
"academic study"
"survey participants"
"research interview"
"participant recruitment"

Combine these with geographic terms:

"United States"
"USA"
"US residents"
"Arizona"
"California"
"Texas"
...
"Canada"
"Ontario"
"Quebec"
"British Columbia"
...

Do not hard-code only a few states.

Generate the geographic query set from the canonical geography database.

---

# 16. AI CLASSIFICATION

Use AI where it provides real value.

Create separate AI capabilities instead of one giant prompt.

Recommended services:

StudyClassificationService
DateExtractionService
GeographyExtractionService
OpportunityExtractionService
DeduplicationService

The AI should extract structured JSON.

Example:

{
"is_research_opportunity": true,
"study_type": "paid survey",
"participant_geo": [
{
"country": "US",
"state": "Arizona",
"city": null
}
],
"published_at": "...",
"reward": "$50",
"duration_minutes": 30,
"eligibility_summary": "...",
"application_url": "...",
"confidence": 0.94
}

Use schema validation.

Do not trust raw AI output without validation.

---

# 17. AI PROVIDER ARCHITECTURE

Create a provider abstraction.

Example:

AIProvider
OpenAIProvider
CompatibleAPIProvider
LocalModelProvider

The application must support changing providers through environment variables/configuration.

Never hard-code API keys.

Provide:

.env.example

Example variables:

DATABASE_URL=
REDIS_URL=
AI_PROVIDER=
AI_API_KEY=
AI_MODEL=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=

Use sensible defaults and clear documentation.

---

# 18. DATABASE

Use PostgreSQL.

Design a normalized database.

Suggested entities:

User
Source
SourceRun
RawDocument
Opportunity
OpportunitySource
Geography
OpportunityGeography
Notification
NotificationDelivery
AlertRule
DiscoveryQuery
AIExtraction
CrawlFailure

Opportunity should contain fields such as:

* id
* title
* normalized_title
* description
* study_type
* source_url
* canonical_url
* application_url
* organization
* published_at
* discovered_at
* last_seen_at
* date_confidence
* original_published_at
* repost_detected
* reward_amount
* reward_currency
* reward_text
* duration_minutes
* eligibility_text
* geography_status
* participant_geo_confidence
* status
* content_hash
* canonical_opportunity_id
* created_at
* updated_at

---

# 19. OPPORTUNITY STATUS

Support statuses such as:

* discovered
* processing
* verified
* eligible
* excluded
* duplicate
* uncertain
* expired
* failed

Only opportunities that are:

verified/eligible
AND
fresh within 7 days
AND
US/Canada eligible

should be eligible for alerting.

---

# 20. NOTIFICATION SYSTEM

Implement notifications.

Start with:

1. Telegram
2. Email

Design it so other channels can be added later.

Create:

NotificationProvider

with:

TelegramNotificationProvider
EmailNotificationProvider

The user should be able to enable/disable each channel.

---

# 21. NOTIFICATION CONTENT

A notification should be concise but useful.

Example:

NEW STUDY FOUND

AI Technology Research Study

Posted: 3 hours ago
Location: Phoenix, Arizona, USA
Type: Paid research study
Reward: $50
Duration: 30 minutes

Eligibility:
Adults living in Phoenix who use AI tools.

Source:
Example Research Platform

Apply:
https://...

Do not send huge scraped page contents.

---

# 22. DO NOT SEND DUPLICATE ALERTS

Track notifications.

For every opportunity:

* has_been_notified
* notification_count
* notification_sent_at
* notified_channels

Do not repeatedly alert for the same opportunity.

If an opportunity materially changes, use a configurable re-alert policy.

---

# 23. DASHBOARD

Build a modern responsive web dashboard.

Recommended frontend:

Next.js/React
TypeScript
Tailwind CSS

The dashboard should have:

## Dashboard home

Show:

* New today
* New in last 24 hours
* New in last 7 days
* US opportunities
* Canada opportunities
* Paid opportunities
* Total discovered
* Duplicates removed
* Failed source runs

## Opportunity list

Each card should display:

* title
* type
* country
* state/province
* city if available
* reward
* duration
* posted time
* source
* freshness
* confidence
* application link

## Filters

Support:

* country
* state
* province
* territory
* city
* study type
* paid/unpaid
* reward
* posted within 24 hours
* posted within 3 days
* posted within 7 days
* source
* remote/in-person

---

# 24. OPPORTUNITY DETAIL PAGE

Display:

Title

Study type

Organization

Posted date

Location

Participant geography

Reward

Duration

Eligibility

Study description

Source

Original link

Application link

Date confidence

Geographic confidence

Discovered timestamp

Source list

Duplicate/related opportunities

---

# 25. SOURCE MANAGEMENT PAGE

Create an admin/source management interface.

Display:

Source name
Status
Last successful crawl
Last attempted crawl
Number of opportunities discovered
Number of valid opportunities
Number of duplicates
Failure count
Average response time

Allow enabling/disabling a source.

---

# 26. SOURCE RUN MONITORING

Create background jobs.

Store:

* start time
* end time
* source
* status
* items fetched
* items parsed
* items rejected
* items accepted
* duplicates
* errors

Support:

* retries
* exponential backoff
* timeouts
* logging

Do not let one broken source stop the whole system.

---

# 27. BACKGROUND TASK SYSTEM

Use:

Redis
+
Celery

Create separate tasks for:

crawl_source
process_document
extract_dates
extract_geography
classify_opportunity
deduplicate_opportunity
verify_freshness
send_notification
cleanup_expired_opportunities

Use scheduled jobs for discovery.

Example scheduling strategy:

High-priority sources:
every 15–30 minutes

Normal sources:
every 1–6 hours

Slow sources:
daily

Make schedules configurable.

Do not hard-code them into application logic.

---

# 28. FRESHNESS CLEANUP

The system should continuously update freshness.

An opportunity can move from:

eligible

to:

expired

after the 7-day window passes.

Expired opportunities should remain in the database for historical analytics but must no longer generate "new opportunity" alerts.

Do not delete them just because they are old.

---

# 29. SEARCH AND DISCOVERY QUERIES

Create a query generator.

It should generate combinations of:

study keywords
+
geographic keywords

Example:

"paid research study" + "Arizona"

"participants needed" + "Ontario"

"user research" + "Toronto"

"survey participants" + "California"

"focus group" + "Canada"

and so on.

Do not manually list every combination.

Build it from databases/configuration.

---

# 30. SEARCH RESULT QUALITY

Search/index results may contain:

* stale dates
* incorrect snippets
* duplicated URLs
* tracking URLs
* pages that no longer exist

Do not consider the search result itself the final source of truth where the original page can be fetched.

Always attempt to inspect the original destination page.

Normalize tracking parameters where appropriate.

Preserve the original URL too.

---

# 31. CRAWLING ENGINE

Use a robust crawler architecture.

Recommended:

HTTP client for normal HTML pages

and

Playwright for JavaScript-rendered pages where permitted.

Implement:

* request timeout
* retry
* content-type validation
* response-size limits
* robots/access checks
* rate limiting
* caching
* duplicate request prevention
* structured extraction
* HTML cleanup

Do not use a browser for everything.

Prefer simple HTTP requests for normal pages and Playwright only where necessary.

---

# 32. CONTENT EXTRACTION

Extract:

* title
* visible text
* metadata
* JSON-LD
* structured timestamps
* links
* canonical URL
* organization
* application links

Store a sanitized copy of the extracted content required for processing.

Do not blindly save enormous HTML documents forever.

---

# 33. STUDY CLASSIFICATION LOGIC

The classifier should identify signals like:

"participants needed"
"seeking participants"
"take part in a study"
"research participants"
"paid survey"
"complete this survey"
"join our study"
"research interview"
"focus group"
"usability testing"
"participant recruitment"

Negative signals:

"research paper"
"journal article"
"academic publication"
"study results"
"research report"
"job posting"
"career opportunity"

The classifier should consider the full context, not merely keyword matching.

---

# 34. REWARD EXTRACTION

Extract reward when available.

Recognize:

$25
$50
US$100
CAD $75
C$50
Amazon gift card $20
gift card
cash incentive
no compensation

Normalize:

reward_amount
reward_currency
reward_type
reward_text

Do not invent a reward if one is not provided.

---

# 35. DURATION EXTRACTION

Recognize:

10 minutes
30 minutes
1 hour
90 minutes
2 sessions
weekly diary
multiple interviews

Normalize to structured duration fields where possible.

---

# 36. ELIGIBILITY EXTRACTION

Extract the explicit participant requirements.

Examples:

Age
Gender if explicitly required
Residence
Occupation
Device usage
Technology usage
Parent status
Industry
Experience
Language
Education
Other explicit requirements

Do not use eligibility data to personalize alerts yet.

The first version should simply display the eligibility information.

Do NOT create an inferred personal profile for me.

---

# 37. USER PROFILE

Keep the user system simple.

Support:

* account
* email
* notification preferences
* Telegram configuration
* timezone
* notification frequency

Do NOT build profile-based matching in version 1.

The only mandatory alert filters are:

* fresh within 7 days
* participant eligibility includes US/Canada

---

# 38. SECURITY

Implement:

* environment-based secrets
* secure authentication
* password hashing
* CSRF protection where applicable
* secure cookies
* API authentication
* rate limiting
* input validation
* SQL injection protection
* XSS protection
* SSRF protection for crawler URLs
* URL validation
* request size limits
* logging of security-relevant events

The crawler must protect against malicious URLs.

Do not allow arbitrary internal network requests through the crawler.

Prevent SSRF against:

* localhost
* private IP ranges
* internal network addresses
* cloud metadata endpoints

---

# 39. API

Build a clean REST API.

Endpoints should include concepts such as:

GET /api/opportunities
GET /api/opportunities/{id}
GET /api/sources
GET /api/stats
GET /api/geographies
GET /api/notifications
POST /api/notifications/test

Use pagination.

Support filtering.

Example:

GET /api/opportunities?country=US&state=Arizona

GET /api/opportunities?country=CA&province=Ontario

GET /api/opportunities?posted_within=7d

---

# 40. OBSERVABILITY

Implement structured logging.

Create useful metrics:

* opportunities discovered
* opportunities rejected
* opportunities accepted
* duplicate rate
* crawl failures
* date extraction failures
* geography extraction failures
* AI extraction failures
* notifications sent
* notifications failed
* average crawl duration
* source freshness

Make debugging easy.

---

# 41. TESTING

Create real automated tests.

Minimum:

Unit tests
Integration tests
API tests
Crawler parser tests
Geography tests
Freshness tests
Deduplication tests
Notification tests

Mandatory freshness test cases:

1. posted 1 hour ago → include
2. posted 1 day ago → include
3. posted 6 days ago → include
4. posted exactly 7 days ago according to configured boundary → handle correctly
5. posted 8 days ago → exclude
6. posted 30 days ago → exclude
7. unknown publication date → no alert
8. deadline is recent but post is old → exclude
9. old original study reposted recently → detect/review
10. new recruitment round → support where verifiable

Mandatory geography tests:

1. United States → include
2. Canada → include
3. Arizona → include
4. Ontario → include
5. Phoenix → include
6. Toronto → include
7. California + Texas → include
8. Quebec + Ontario → include
9. US nationwide → include
10. Canadian nationwide → include
11. global study allowing US/Canada → include
12. UK only → exclude
13. Australia only → exclude
14. US researcher but participants in Europe → exclude
15. Canada researcher but participants worldwide → include only if US/Canada eligibility is explicit
16. "remote" without geography → do not assume eligibility
17. researcher location is US but participant geography unknown → do not assume US eligibility

---

# 42. TEST FIXTURES

Create realistic fixture documents for:

* Arizona study
* California survey
* Texas focus group
* Ontario research study
* Toronto user interview
* Canada-wide survey
* US-wide survey
* US + Canada study
* global survey that includes US/Canada
* old study
* reposted study
* unknown date study
* researcher in US but participants abroad
* duplicate study on multiple domains

Tests must prove that the filtering system works correctly.

---

# 43. DATA QUALITY / CONFIDENCE

Every extraction should have a confidence score.

For example:

date_confidence
geography_confidence
classification_confidence

Use deterministic rules to override bad AI guesses where necessary.

High confidence:

0.90–1.00

Medium:

0.70–0.89

Low:

below 0.70

Make thresholds configurable.

Do not alert low-confidence opportunities.

---

# 44. IMPORTANT FALSE-POSITIVE PREVENTION

This product is valuable only if notifications are useful.

Prioritize precision over sending everything.

Do NOT send an alert simply because:

* the word "study" appears
* the researcher is in the US
* the company is in Canada
* the page contains a US city unrelated to participant eligibility
* the deadline is within 7 days
* the study is old but recently updated
* a search result says "recent" without a reliable source date

Require enough evidence to support:

1. It is a research participation opportunity.
2. It is within the 7-day publication window.
3. Participants from the US/Canada are eligible.

---

# 45. PROJECT STRUCTURE

Use a clean professional architecture.

Suggested backend:

backend/
config/
apps/
opportunities/
sources/
crawling/
classification/
geography/
notifications/
users/
analytics/
tasks/
tests/
manage.py

Suggested frontend:

frontend/
app/
components/
features/
hooks/
lib/
services/
types/
styles/

Also include:

scripts/
docker/
docs/
tests/

You may improve this structure if there is a better architecture.

Keep responsibilities separated.

---

# 46. DOCKER

Provide:

docker-compose.yml

Services should include at minimum:

* backend
* frontend
* postgres
* redis
* worker
* scheduler

Optional:

* monitoring service

The entire development environment should be runnable with one documented command.

---

# 47. DOCUMENTATION

Create:

README.md

ARCHITECTURE.md

API.md

SOURCE_CONNECTORS.md

DATA_MODEL.md

DEPLOYMENT.md

CRAWLER_COMPLIANCE.md

TESTING.md

ENVIRONMENT.md

Include exact commands.

---

# 48. ENVIRONMENT

Provide:

.env.example

Do not commit real secrets.

Explain every environment variable.

---

# 49. INITIAL DEVELOPMENT STRATEGY

Do not attempt to build 100 source connectors immediately.

Build the platform around a scalable connector interface.

Version 1 should prove that the entire pipeline works end-to-end.

Start with a small number of legally/technically appropriate sources and make the architecture capable of adding many more.

The important thing is:

SOURCE → DISCOVERY → EXTRACTION → FILTERING → DATABASE → NOTIFICATION → DASHBOARD

must work completely.

---

# 50. ADMIN / DEBUG TOOLS

Create internal tools that let me inspect:

* raw discovered item
* extracted date
* extracted geography
* classification result
* confidence scores
* duplicate decision
* source URL
* reason for exclusion
* notification decision

For every rejected item, store a reason such as:

EXCLUDED:

* not a study
* too old
* geography unknown
* outside US/Canada
* duplicate
* invalid page
* no reliable publication date

This is very important for debugging the system.

---

# 51. MANUAL INGESTION TOOL

Create an internal admin feature where I can paste a URL.

The system should:

1. fetch the URL
2. extract the page
3. classify it
4. extract date
5. extract geography
6. determine whether it qualifies
7. show the result
8. allow saving it

This will make development/testing much easier.

---

# 52. SEARCH/QUERY PAGE

Add a dashboard search page.

I should be able to search:

"Arizona studies"

"Toronto surveys"

"Canada focus groups"

"California paid research"

"US usability studies"

etc.

Use the normalized geography data rather than only raw keyword matching.

---

# 53. ALERT RULE

The first production alert rule should essentially be:

IF

is_research_opportunity == TRUE

AND

published_at is within 7 days

AND

participant_geography includes US or Canada

AND

geography_confidence >= configured_threshold

AND

date_confidence >= configured_threshold

AND

not duplicate

AND

not already notified

THEN

send notification.

Otherwise:

do not send notification.

---

# 54. TIMEZONE

Store timestamps in UTC.

The UI should convert them to the user's configured timezone.

The user should be able to set:

Africa/Lagos

or any valid timezone.

Do not rely on the server's local timezone.

---

# 55. PERFORMANCE

Design for growth.

The system should eventually be able to process thousands of candidates per day.

Use:

* asynchronous/background processing
* Redis
* Celery
* batching where useful
* database indexes
* caching
* connection pooling
* source-specific rate limits

Do not perform expensive AI processing synchronously during a web request.

---

# 56. COST CONTROL

AI can become expensive.

Do not send every raw page directly to an expensive model.

Use a staged pipeline:

Stage 1:
cheap deterministic filtering

Stage 2:
rule-based extraction

Stage 3:
AI only when necessary

Stage 4:
high-confidence validation

Cache AI results where possible.

Do not repeatedly process the same document.

---

# 57. RATE LIMITING / RETRIES

Every source connector should have configurable:

* requests per minute
* concurrency
* timeout
* retry count
* exponential backoff

A failed source should not crash the worker or block other sources.

---

# 58. USER EXPERIENCE

The UI should look like a professional SaaS product.

It should be:

* clean
* modern
* fast
* responsive
* mobile friendly
* easy to scan

Opportunity cards should make the freshness obvious.

Example:

NEW — 2 hours ago

or:

5 days ago

Anything older than 7 days should not appear in the active/new opportunities feed.

---

# 59. PRIMARY DASHBOARD METRICS

Show:

New in last 24h

New in last 7 days

US opportunities

Canada opportunities

Paid opportunities

Unpaid opportunities

Sources monitored

Successful source runs

Failed source runs

Duplicates removed

---

# 60. FUTURE-READY ARCHITECTURE

Do not implement these as core requirements yet, but design the architecture so they can be added later:

* user profiles
* personalized eligibility matching
* browser extension
* mobile app
* AI summaries
* automatic opportunity scoring
* opportunity history
* analytics
* recommendation engine
* SMS notifications
* Discord notifications
* Slack notifications
* multiple users
* paid SaaS plans
* team accounts

Do not let these future features complicate version 1 unnecessarily.

---

# 61. MVP ACCEPTANCE CRITERIA

The MVP is not complete until all of the following work:

1. A source can be crawled.
2. A candidate opportunity can be extracted.
3. The system can determine whether it is a research opportunity.
4. The system can identify the publication date.
5. The system can determine whether the publication date is within 7 days.
6. The system can identify US/Canada participant geography.
7. The system can distinguish participant geography from organization geography.
8. The system can recognize states/provinces/cities/regions.
9. The system can deduplicate opportunities.
10. The system can save normalized opportunities to PostgreSQL.
11. The system can expose them through an API.
12. The dashboard can display them.
13. Telegram notifications work.
14. Email notifications work.
15. Old studies do not trigger alerts.
16. Unknown-date studies do not trigger alerts.
17. Non-US/Canada opportunities do not trigger alerts.
18. Duplicate studies do not produce duplicate notifications.
19. Background workers and scheduler work.
20. Docker development setup works.
21. Automated tests pass.
22. Documentation is complete.

---

# 62. DEVELOPMENT METHOD

Work autonomously and continuously.

Do NOT stop after creating boilerplate.

Do NOT merely describe what should be built.

Actually create the files, code, migrations, tests, configuration, Docker setup, and UI.

Implement the project in logical phases.

Phase 1:
Architecture + repository structure

Phase 2:
Database + models

Phase 3:
Source adapter architecture

Phase 4:
Crawler

Phase 5:
Date extraction

Phase 6:
Geography engine

Phase 7:
Study classification

Phase 8:
Deduplication

Phase 9:
Celery/Redis scheduling

Phase 10:
Notifications

Phase 11:
REST API

Phase 12:
Frontend dashboard

Phase 13:
Testing

Phase 14:
Documentation

Phase 15:
End-to-end verification

After each major phase, run the relevant tests.

Fix errors instead of leaving TODO placeholders.

---

# 63. IMPORTANT IMPLEMENTATION PRINCIPLES

Prefer maintainability over cleverness.

Prefer deterministic logic where deterministic logic is reliable.

Use AI only where it adds value.

Do not hard-code assumptions about geography.

Do not hard-code only a handful of sources.

Do not hard-code only a handful of US states.

Do not hard-code only a handful of Canadian provinces.

Generate geography from canonical datasets/configuration.

Use typed schemas.

Validate external data.

Handle malformed pages safely.

Handle network failures.

Handle timeouts.

Handle duplicate content.

Handle stale content.

Handle missing dates.

Handle ambiguous geography.

Handle JavaScript-heavy pages where permitted.

Make every connector independently testable.

---

# 64. FIRST BUILD TASK

Start by inspecting the existing project directory and environment.

Determine whether this is a new empty project or an existing repository.

Do not destroy existing user code without reason.

Then create the Study Radar architecture.

Use a monorepo if appropriate.

Choose stable/current versions of the selected frameworks that are compatible with the environment.

Use:

Backend:
Django + Django REST Framework

Database:
PostgreSQL

Background processing:
Celery + Redis

Frontend:
Next.js + React + TypeScript + Tailwind

Crawler:
HTTP client + Playwright where required

Testing:
Pytest + appropriate frontend test tooling

Containerization:
Docker + Docker Compose

You may make reasonable technical improvements to this stack, but preserve the core architecture and requirements above.

---

# 65. FINAL EXPECTATION

At the end of implementation, I should have a working application where the system continuously discovers research studies and surveys, identifies whether they are actually participant opportunities, determines their original publication date, determines the participant geographic eligibility, filters to the United States and Canada, recognizes nationwide and state/province/city/region-specific opportunities, excludes anything older than 7 days, removes duplicates, stores the normalized records, displays them in a dashboard, and sends me notifications for qualifying fresh opportunities.

The most important principle is:

> I should no longer have to manually search social media and the web every day just to find newly posted US and Canada research studies and surveys.

Build the product around that goal.

Do not finish at the planning stage.

Start implementing.