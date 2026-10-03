import socket
import ipaddress
import hashlib
import json
import logging
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from django.conf import settings

logger = logging.getLogger(__name__)

class SSRFSecurityError(Exception):
    """Raised when a requested URL resolves to a forbidden private/internal IP address."""
    pass

class CrawlEngine:
    def __init__(self, timeout=None, user_agent=None):
        self.timeout = timeout or getattr(settings, 'CRAWLER_DEFAULT_TIMEOUT', 15)
        self.user_agent = user_agent or getattr(settings, 'CRAWLER_USER_AGENT', 'StudyRadarBot/1.0')

    @classmethod
    def validate_url_safety(cls, url: str) -> None:
        """
        Validate URL for SSRF protection:
        Ensures scheme is http/https and domain does NOT resolve to internal/private/loopback addresses.
        """
        if not getattr(settings, 'SSRF_PROTECTION_ENABLED', True):
            return

        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            raise SSRFSecurityError(f"Disallowed URL scheme: '{parsed.scheme}'. Only http and https are permitted.")

        hostname = parsed.hostname
        if not hostname:
            raise SSRFSecurityError("URL does not contain a valid hostname.")

        if hostname.lower() in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
            raise SSRFSecurityError("Access to localhost is prohibited.")

        try:
            # Resolve all IP addresses for hostname
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                ip_obj = ipaddress.ip_address(ip_str)
                if (
                    ip_obj.is_private or
                    ip_obj.is_loopback or
                    ip_obj.is_link_local or
                    ip_obj.is_reserved or
                    ip_obj.is_multicast
                ):
                    raise SSRFSecurityError(f"URL resolves to restricted IP address: {ip_str}")
        except socket.gaierror as e:
            raise SSRFSecurityError(f"DNS resolution failed for {hostname}: {str(e)}")

    def fetch_page(self, url: str) -> dict:
        """
        Safely fetch an HTML page or API endpoint with SSRF checks, headers, and size limits.
        """
        self.validate_url_safety(url)

        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=self.timeout,
            stream=True,
            allow_redirects=True
        )

        # Enforce maximum response size (e.g. 5 MB)
        max_bytes = 5 * 1024 * 1024
        content_bytes = bytearray()
        for chunk in response.iter_content(chunk_size=16384):
            content_bytes.extend(chunk)
            if len(content_bytes) > max_bytes:
                break

        final_url = response.url
        self.validate_url_safety(final_url)

        content_text = content_bytes.decode('utf-8', errors='replace')
        content_hash = hashlib.sha256(content_text.encode('utf-8')).hexdigest()

        return {
            'url': url,
            'final_url': final_url,
            'status_code': response.status_code,
            'content_type': response.headers.get('Content-Type', ''),
            'raw_content': content_text,
            'content_hash': content_hash,
        }

    def parse_html_document(self, html_text: str, base_url: str) -> dict:
        """
        Extract structured metadata, JSON-LD, title, clean body text, and links.
        """
        soup = BeautifulSoup(html_text, 'html.parser')

        # Extract title
        title = ''
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        og_title = soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'og:title'})
        if og_title and og_title.get('content'):
            title = og_title['content'].strip()

        # Extract JSON-LD metadata
        json_ld_data = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                if script.string:
                    data = json.loads(script.string)
                    json_ld_data.append(data)
            except Exception:
                continue

        # Extract OpenGraph / Meta information
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('itemprop')
            content = meta.get('content')
            if name and content:
                meta_tags[name.lower()] = content.strip()

        # Extract canonical URL if present
        canonical_tag = soup.find('link', rel='canonical')
        canonical_url = canonical_tag['href'].strip() if canonical_tag and canonical_tag.get('href') else base_url

        # Remove scripts, styles, forms, and irrelevant markup for clean text extraction
        for element in soup(['script', 'style', 'nav', 'footer', 'noscript', 'svg']):
            element.decompose()

        clean_text = soup.get_text(separator=' ', strip=True)

        return {
            'title': title,
            'canonical_url': canonical_url,
            'json_ld': json_ld_data,
            'meta_tags': meta_tags,
            'clean_text': clean_text[:20000],  # Bound text size for downstream analysis
        }
