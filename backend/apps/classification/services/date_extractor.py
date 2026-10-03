import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
import dateparser
from dateutil import parser as dateutil_parser
from apps.opportunities.models import DatePrecision

class DateExtractionResult:
    def __init__(
        self,
        published_at: Optional[datetime] = None,
        published_at_timezone: str = 'UTC',
        precision: str = DatePrecision.UNKNOWN,
        source: str = 'none',
        confidence: float = 0.0,
        original_published_at: Optional[datetime] = None,
        is_deadline_confused: bool = False,
        raw_match: str = ''
    ):
        self.published_at = published_at
        self.published_at_timezone = published_at_timezone
        self.precision = precision
        self.source = source
        self.confidence = confidence
        self.original_published_at = original_published_at
        self.is_deadline_confused = is_deadline_confused
        self.raw_match = raw_match

    def to_dict(self) -> Dict[str, Any]:
        return {
            'published_at': self.published_at,
            'published_at_timezone': self.published_at_timezone,
            'published_date_precision': self.precision,
            'date_source': self.source,
            'date_confidence': self.confidence,
            'original_published_at': self.original_published_at,
            'raw_match': self.raw_match,
        }

class DateExtractionService:
    """
    Intelligent date extractor that adheres strictly to Section 4 of instruction.md.
    Prefers explicit publication dates, structured JSON-LD/meta, relative dates,
    and strictly avoids confusing publication date with deadlines.
    """

    META_DATE_KEYS = [
        'article:published_time',
        'og:published_time',
        'publication_date',
        'datepublished',
        'publishdate',
        'pubdate',
        'dc.date.issued',
        'parsely-pub-date',
        'sailthru.date',
    ]

    UPDATE_DATE_KEYS = [
        'article:modified_time',
        'og:updated_time',
        'datemodified',
        'lastmodified',
    ]

    # Explicit regex patterns for post dates
    POST_PATTERNS = [
        # "Posted 3 hours ago", "Published 2 days ago", "Posted yesterday"
        (re.compile(r'(?:posted|published|added|created)\s*:\s*(\d+\s+(?:minutes?|hours?|days?|weeks?)\s+ago)', re.IGNORECASE), DatePrecision.RELATIVE_DATETIME, 0.95),
        (re.compile(r'(?:posted|published|added)\s+(\d+\s+(?:minutes?|hours?|days?|weeks?)\s+ago)', re.IGNORECASE), DatePrecision.RELATIVE_DATETIME, 0.95),
        (re.compile(r'(?:posted|published)\s*:\s*(yesterday|today)', re.IGNORECASE), DatePrecision.RELATIVE_DATE, 0.92),
        (re.compile(r'(?:posted|published|date)\s*:\s*([A-Za-z]+ \d{1,2},?\s*\d{4})', re.IGNORECASE), DatePrecision.EXACT_DATE, 0.95),
        (re.compile(r'(?:posted|published|date)\s*:\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})', re.IGNORECASE), DatePrecision.EXACT_DATE, 0.95),
        (re.compile(r'(?:posted|published|date)\s*:\s*(\d{4}-\d{2}-\d{2})', re.IGNORECASE), DatePrecision.EXACT_DATE, 0.95),
        (re.compile(r'published\s+on\s+([A-Za-z]+ \d{1,2},?\s*\d{4})', re.IGNORECASE), DatePrecision.EXACT_DATE, 0.92),
        (re.compile(r'posted\s+on\s+([A-Za-z]+ \d{1,2},?\s*\d{4})', re.IGNORECASE), DatePrecision.EXACT_DATE, 0.92),
    ]

    # Deadline patterns to avoid mistaking for published_at
    DEADLINE_PATTERNS = [
        re.compile(r'(?:deadline|closes|apply by|closing date|submission deadline|expires)\s*:\s*([^\n\.,]+)', re.IGNORECASE),
    ]

    def extract_date(
        self,
        text_content: str = '',
        meta_tags: Optional[Dict[str, str]] = None,
        json_ld: Optional[list] = None,
        feed_timestamp: Optional[datetime] = None,
        reference_time: Optional[datetime] = None
    ) -> DateExtractionResult:
        now = reference_time or datetime.now(timezone.utc)
        meta_tags = meta_tags or {}
        json_ld = json_ld or []

        # 1. Check JSON-LD structured data for datePublished
        for item in json_ld:
            if isinstance(item, dict):
                date_published_str = item.get('datePublished') or item.get('dateCreated')
                if date_published_str and isinstance(date_published_str, str):
                    parsed_dt = self._parse_iso_or_string(date_published_str, now)
                    if parsed_dt:
                        return DateExtractionResult(
                            published_at=parsed_dt,
                            published_at_timezone='UTC',
                            precision=DatePrecision.EXACT_DATETIME if 'T' in date_published_str else DatePrecision.EXACT_DATE,
                            source='json_ld',
                            confidence=0.98,
                            raw_match=date_published_str
                        )

        # 2. Check OpenGraph and HTML meta tags
        for key in self.META_DATE_KEYS:
            if key in meta_tags and meta_tags[key]:
                raw_val = meta_tags[key]
                parsed_dt = self._parse_iso_or_string(raw_val, now)
                if parsed_dt:
                    return DateExtractionResult(
                        published_at=parsed_dt,
                        published_at_timezone='UTC',
                        precision=DatePrecision.EXACT_DATETIME if 'T' in raw_val else DatePrecision.EXACT_DATE,
                        source=f'meta:{key}',
                        confidence=0.95,
                        raw_match=raw_val
                    )

        # 3. Check explicit RSS/Atom feed publication timestamp
        if feed_timestamp:
            normalized_dt = feed_timestamp if feed_timestamp.tzinfo else feed_timestamp.replace(tzinfo=timezone.utc)
            return DateExtractionResult(
                published_at=normalized_dt,
                published_at_timezone='UTC',
                precision=DatePrecision.EXACT_DATETIME,
                source='feed_timestamp',
                confidence=0.96,
                raw_match=str(feed_timestamp)
            )

        # 4. Check explicit text regex patterns (e.g. "Posted 3 hours ago", "Published October 2, 2026")
        for pattern, precision, conf in self.POST_PATTERNS:
            match = pattern.search(text_content)
            if match:
                date_str = match.group(1).strip()
                parsed_dt = dateparser.parse(
                    date_str,
                    settings={'RELATIVE_BASE': now, 'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True}
                )
                if parsed_dt:
                    return DateExtractionResult(
                        published_at=parsed_dt,
                        published_at_timezone='UTC',
                        precision=precision,
                        source='text_pattern',
                        confidence=conf,
                        raw_match=date_str
                    )

        # 5. Check if page only has modified/update date
        for key in self.UPDATE_DATE_KEYS:
            if key in meta_tags and meta_tags[key]:
                raw_val = meta_tags[key]
                parsed_dt = self._parse_iso_or_string(raw_val, now)
                if parsed_dt:
                    # Stored as uncertain/approximate with lower confidence as required by Section 4
                    return DateExtractionResult(
                        published_at=parsed_dt,
                        published_at_timezone='UTC',
                        precision=DatePrecision.APPROXIMATE,
                        source=f'modified_meta_uncertain:{key}',
                        confidence=0.50,  # Below alert threshold so it won't falsely trigger alert
                        raw_match=raw_val
                    )

        # 6. Check if only deadline was found (should NOT be used as published_at!)
        for pattern in self.DEADLINE_PATTERNS:
            match = pattern.search(text_content)
            if match:
                return DateExtractionResult(
                    published_at=None,
                    precision=DatePrecision.UNKNOWN,
                    source='deadline_detected_excluded',
                    confidence=0.0,
                    is_deadline_confused=True,
                    raw_match=match.group(0)
                )

        # Default: date unknown
        return DateExtractionResult(
            published_at=None,
            precision=DatePrecision.UNKNOWN,
            source='none',
            confidence=0.0
        )

    def _parse_iso_or_string(self, date_str: str, now: datetime) -> Optional[datetime]:
        try:
            dt = dateutil_parser.parse(date_str)
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt
        except Exception:
            try:
                parsed = dateparser.parse(
                    date_str,
                    settings={'RELATIVE_BASE': now, 'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True}
                )
                return parsed
            except Exception:
                return None
