import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import Optional, Tuple
from django.db.models import Q
from apps.opportunities.models import Opportunity, OpportunityStatus, OpportunitySource
from apps.sources.models import Source

class DeduplicationService:
    """
    Multi-level deduplication and repost detector adhering to Sections 11 & 12.
    Detects duplicates by normalized URL, content hash, title + organization matching,
    and links multiple source sightings under a single canonical opportunity record.
    """

    TRACKING_PARAMS = {
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'fbclid', 'gclid', 'ref', 'source', 'mc_cid', 'mc_eid'
    }

    @classmethod
    def normalize_url(cls, raw_url: str) -> str:
        """Strip tracking parameters, query fragments, and standardize scheme & netloc."""
        if not raw_url:
            return ''
        try:
            parsed = urlparse(raw_url.strip())
            # Filter tracking parameters
            filtered_queries = [
                (k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=False)
                if k.lower() not in cls.TRACKING_PARAMS
            ]
            normalized_query = urlencode(sorted(filtered_queries))
            # Remove trailing slash from path for consistency
            path = parsed.path.rstrip('/')
            return urlunparse((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                path,
                parsed.params,
                normalized_query,
                ''  # Strip fragment
            ))
        except Exception:
            return raw_url.strip()

    @classmethod
    def normalize_title(cls, title: str) -> str:
        """Normalize study titles for string similarity matching."""
        if not title:
            return ''
        # Convert to lower, strip non-alphanumeric (keep spaces)
        cleaned = re.sub(r'[^\w\s]', ' ', title.lower())
        # Collapse multiple spaces
        return " ".join(cleaned.split())

    def find_duplicate(
        self,
        source_url: str,
        canonical_url: str,
        content_hash: str,
        title: str,
        organization: str = ''
    ) -> Tuple[Optional[Opportunity], str]:
        """
        Multi-level duplicate search:
        1. Exact URL match or Normalized URL match
        2. Content hash match
        3. Normalized title + organization match
        Returns (canonical_opportunity, match_reason) or (None, '')
        """
        norm_source_url = self.normalize_url(source_url)
        norm_canonical_url = self.normalize_url(canonical_url)
        norm_title = self.normalize_title(title)

        # Level 1: Match by normalized URL
        if norm_canonical_url:
            url_match = Opportunity.objects.filter(
                Q(canonical_url=norm_canonical_url) | Q(source_url=norm_canonical_url)
            ).first()
            if url_match:
                return (url_match.canonical_opportunity or url_match, "canonical_url_match")

        if norm_source_url:
            source_url_match = Opportunity.objects.filter(
                Q(source_url=norm_source_url) | Q(canonical_url=norm_source_url)
            ).first()
            if source_url_match:
                return (source_url_match.canonical_opportunity or source_url_match, "source_url_match")

        # Level 2: Match by exact content hash
        if content_hash:
            hash_match = Opportunity.objects.filter(content_hash=content_hash).first()
            if hash_match:
                return (hash_match.canonical_opportunity or hash_match, "content_hash_match")

        # Level 3: Match by normalized title (and organization if available)
        if norm_title and len(norm_title) > 15:
            qs = Opportunity.objects.filter(normalized_title=norm_title)
            if organization:
                org_match = qs.filter(organization__iexact=organization).first()
                if org_match:
                    return (org_match.canonical_opportunity or org_match, "title_and_organization_match")
            title_match = qs.first()
            if title_match:
                return (title_match.canonical_opportunity or title_match, "title_match")

        return None, ''

    def record_opportunity(
        self,
        opportunity_data: dict,
        source: Source,
        raw_document=None
    ) -> Tuple[Opportunity, bool, str]:
        """
        Creates a new canonical opportunity or attaches as an additional source to an existing one.
        Returns: (opportunity, is_new_study, decision_reason)
        """
        source_url = opportunity_data.get('source_url', '')
        canonical_url = opportunity_data.get('canonical_url', '') or source_url
        content_hash = opportunity_data.get('content_hash', '')
        title = opportunity_data.get('title', '')
        organization = opportunity_data.get('organization', '')
        published_at = opportunity_data.get('published_at')

        existing_canonical, reason = self.find_duplicate(
            source_url=source_url,
            canonical_url=canonical_url,
            content_hash=content_hash,
            title=title,
            organization=organization
        )

        if existing_canonical:
            # Duplicate found! Attach this source sighting under the canonical opportunity
            OpportunitySource.objects.get_or_create(
                opportunity=existing_canonical,
                source=source,
                source_url=source_url,
                defaults={'raw_document': raw_document}
            )

            # Check for reposting of old study (Section 12)
            if existing_canonical.published_at and published_at:
                if published_at > existing_canonical.published_at:
                    # New sighting timestamp is later: mark as repost, preserve original published_at
                    existing_canonical.repost_detected = True
                    if not existing_canonical.original_published_at:
                        existing_canonical.original_published_at = existing_canonical.published_at
                    existing_canonical.save(update_fields=['repost_detected', 'original_published_at', 'last_seen_at'])

            return existing_canonical, False, f"Duplicate attached to existing study ({reason})"

        # Brand new study opportunity: create new canonical record
        norm_title = self.normalize_title(title)
        norm_source_url = self.normalize_url(source_url)
        norm_canonical_url = self.normalize_url(canonical_url)

        opportunity = Opportunity.objects.create(
            title=title,
            normalized_title=norm_title,
            description=opportunity_data.get('description', ''),
            study_type=opportunity_data.get('study_type', 'research_study'),
            source_url=norm_source_url,
            canonical_url=norm_canonical_url,
            application_url=opportunity_data.get('application_url', '') or norm_source_url,
            organization=organization,
            researcher_location=opportunity_data.get('researcher_location', ''),
            published_at=published_at,
            published_at_timezone=opportunity_data.get('published_at_timezone', 'UTC'),
            published_date_precision=opportunity_data.get('published_date_precision', 'unknown'),
            date_source=opportunity_data.get('date_source', 'unknown'),
            date_confidence=opportunity_data.get('date_confidence', 0.0),
            reward_amount=opportunity_data.get('reward_amount'),
            reward_currency=opportunity_data.get('reward_currency', 'USD'),
            reward_text=opportunity_data.get('reward_text', ''),
            reward_type=opportunity_data.get('reward_type', ''),
            is_paid=opportunity_data.get('is_paid', False),
            duration_minutes=opportunity_data.get('duration_minutes'),
            duration_text=opportunity_data.get('duration_text', ''),
            eligibility_text=opportunity_data.get('eligibility_text', ''),
            geography_status=opportunity_data.get('geography_status', 'unknown'),
            participant_geo_confidence=opportunity_data.get('participant_geo_confidence', 0.0),
            status=opportunity_data.get('status', OpportunityStatus.VERIFIED),
            exclusion_reason=opportunity_data.get('exclusion_reason', ''),
            content_hash=content_hash,
        )

        OpportunitySource.objects.create(
            opportunity=opportunity,
            source=source,
            source_url=norm_source_url,
            raw_document=raw_document
        )

        return opportunity, True, "New canonical opportunity created"
