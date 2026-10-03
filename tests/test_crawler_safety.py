import pytest
from apps.crawling.services.crawler import CrawlEngine, SSRFSecurityError

class TestCrawlerSafetyAndSSRF:
    def test_blocks_localhost(self):
        with pytest.raises(SSRFSecurityError):
            CrawlEngine.validate_url_safety("http://localhost:8000/internal-admin")

    def test_blocks_127_0_0_1(self):
        with pytest.raises(SSRFSecurityError):
            CrawlEngine.validate_url_safety("http://127.0.0.1:5432")

    def test_blocks_private_ip(self):
        with pytest.raises(SSRFSecurityError):
            CrawlEngine.validate_url_safety("http://192.168.1.100/config")

    def test_blocks_cloud_metadata_ip(self):
        with pytest.raises(SSRFSecurityError):
            CrawlEngine.validate_url_safety("http://169.254.169.254/latest/meta-data")

    def test_blocks_invalid_scheme(self):
        with pytest.raises(SSRFSecurityError):
            CrawlEngine.validate_url_safety("file:///etc/passwd")

    def test_allows_public_https_url(self, monkeypatch):
        # Mock getaddrinfo to return a valid public IPv4 address
        def mock_getaddrinfo(host, port):
            return [(2, 1, 6, '', ('93.184.216.34', 0))]
        monkeypatch.setattr("socket.getaddrinfo", mock_getaddrinfo)
        CrawlEngine.validate_url_safety("https://dsl.harvard.edu/participate")
