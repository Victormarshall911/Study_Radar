# Crawler Compliance & Security Architecture

Study Radar strictly complies with Section 14 and Section 38 of the product requirements.

---

## 1. Compliance Principles
- **Authorized & Public Methods Only**: Ingestion is restricted to public web pages, permitted RSS/Atom feeds, sitemaps, and official APIs.
- **Strict Prohibition Against Bypassing Controls**:
  - NO CAPTCHA evasion.
  - NO paywall circumvention.
  - NO fake account creation or authentication evasion.
  - NO header spoofing to impersonate browsers in bad faith.
- **Respect for Rate Limits & Robots.txt**:
  - Configurable rate limits per source (`rate_limit_rps`, default 1.0 req/sec).
  - Polite User-Agent identification:
    `StudyRadarBot/1.0 (+https://studyradar.local/bot; contact@studyradar.local)`
  - Configurable backoff and timeouts.

---

## 2. Server-Side Request Forgery (SSRF) Protection
To prevent malicious exploitation when ingesting user-submitted or discovered URLs, the `CrawlEngine` enforces strict pre-flight security checks:
- **Disallowed Schemes**: Only `http` and `https` schemes are permitted. Schemes such as `file://`, `gopher://`, `ftp://` are rejected immediately.
- **IP Address Resolution & Blacklisting**:
  Before any network socket is opened, the hostname is resolved to its IP addresses. The request is aborted with an `SSRFSecurityError` if any IP belongs to:
  - Loopback (`127.0.0.0/8`, `::1`)
  - Private IP ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
  - Cloud Metadata endpoints (`169.254.169.254`, Link-local)
  - Multicast and reserved ranges.
- **Maximum Payload Size Limit**: Responses are capped at 5 MB to prevent resource exhaustion attacks.
