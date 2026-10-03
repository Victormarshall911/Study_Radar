import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from apps.opportunities.models import GeographyStatus
from apps.geography.models import GeographyScope

class GeoMatch:
    def __init__(
        self,
        country: str,
        state_province: Optional[str] = None,
        state_code: Optional[str] = None,
        city: Optional[str] = None,
        scope: str = GeographyScope.UNKNOWN,
        confidence: float = 1.0,
        is_explicit: bool = True,
        match_text: str = ''
    ):
        self.country = country
        self.state_province = state_province
        self.state_code = state_code
        self.city = city
        self.scope = scope
        self.confidence = confidence
        self.is_explicit = is_explicit
        self.match_text = match_text

    def to_dict(self) -> Dict[str, Any]:
        return {
            'country': self.country,
            'state_province': self.state_province,
            'state_code': self.state_code,
            'city': self.city,
            'scope': self.scope,
            'confidence': self.confidence,
            'is_explicit': self.is_explicit,
            'match_text': self.match_text,
        }

class GeographicResolutionResult:
    def __init__(
        self,
        geography_status: str,
        participant_geo_confidence: float,
        matches: List[GeoMatch],
        participant_locations: List[str],
        researcher_locations: List[str],
        is_eligible_us_or_ca: bool,
        case_reason: str
    ):
        self.geography_status = geography_status
        self.participant_geo_confidence = participant_geo_confidence
        self.matches = matches
        self.participant_locations = participant_locations
        self.researcher_locations = researcher_locations
        self.is_eligible_us_or_ca = is_eligible_us_or_ca
        self.case_reason = case_reason

class GeographyResolver:
    """
    Hybrid Geographic Engine adhering strictly to Sections 5-10 of instruction.md.
    Distinguishes participant location from researcher location,
    evaluates all 15 decision logic cases, and matches against canonical gazetteer.
    """

    def __init__(self, gazetteer_path: Optional[Path] = None):
        if not gazetteer_path:
            gazetteer_path = Path(__file__).resolve().parent.parent / 'data' / 'canonical_gazetteer.json'
        with open(gazetteer_path, 'r', encoding='utf-8') as f:
            self.gazetteer = json.load(f)

        self._build_lookup_indexes()

    def _build_lookup_indexes(self):
        # Index US states
        self.us_state_by_name = {s['name'].lower(): s for s in self.gazetteer['us_states']}
        self.us_state_by_code = {s['code'].lower(): s for s in self.gazetteer['us_states']}

        # Index Canadian provinces & territories
        self.ca_prov_by_name = {p['name'].lower(): p for p in self.gazetteer['ca_provinces']}
        self.ca_prov_by_name.update({t['name'].lower(): t for t in self.gazetteer['ca_territories']})
        self.ca_prov_by_code = {p['code'].lower(): p for p in self.gazetteer['ca_provinces']}
        self.ca_prov_by_code.update({t['code'].lower(): t for t in self.gazetteer['ca_territories']})

        # Excluded countries list
        self.excluded_countries = [c.lower() for c in self.gazetteer.get('excluded_foreign_countries', [])]

    def resolve(
        self,
        title: str,
        text_content: str,
        eligibility_text: str = '',
        meta_tags: Optional[Dict[str, str]] = None
    ) -> GeographicResolutionResult:
        combined_text = f"{title} {eligibility_text} {text_content}".strip()
        
        # 1. Distinguish participant location cues from researcher/org cues
        # Dedicated participant signals: "looking for people living in", "residents of", "participants from", "open to adults in"
        participant_context, researcher_context = self._split_participant_and_researcher_contexts(combined_text)

        # 2. Check for explicit foreign exclusions (Case 14: UK only, Australia only, Europe only)
        if self._is_strictly_foreign(participant_context):
            return GeographicResolutionResult(
                geography_status=GeographyStatus.OUTSIDE_TARGET,
                participant_geo_confidence=0.95,
                matches=[],
                participant_locations=[],
                researcher_locations=[],
                is_eligible_us_or_ca=False,
                case_reason="Case 14: Opportunity strictly restricted to country outside US/Canada"
            )

        matches: List[GeoMatch] = []
        is_us = False
        is_ca = False

        # 3. Check for Nationwide US signals (Case 1)
        us_nationwide_pattern = re.compile(
            r'\b(?:adults\s+across\s+the\s+united\s+states|us\s+residents\s+only|united\s+states\s+residents|across\s+the\s+us|nationwide\s*\(us\)|us\s+nationwide|living\s+anywhere\s+in\s+the\s+us|in\s+the\s+united\s+states|us\s+participants|united\s+states)\b',
            re.IGNORECASE
        )
        if us_nationwide_pattern.search(participant_context):
            is_us = True
            matches.append(GeoMatch(country='US', scope=GeographyScope.NATIONWIDE, confidence=0.98, match_text='US Nationwide'))

        # 4. Check for Nationwide Canada signals (Case 2)
        ca_nationwide_pattern = re.compile(
            r'\b(?:adults\s+living\s+anywhere\s+in\s+canada|canadian\s+residents|across\s+canada|canada-wide|nationwide\s*\(canada\)|canadian\s+participants|in\s+canada|canada)\b',
            re.IGNORECASE
        )
        if ca_nationwide_pattern.search(participant_context):
            is_ca = True
            matches.append(GeoMatch(country='CA', scope=GeographyScope.NATIONWIDE, confidence=0.98, match_text='Canada Nationwide'))

        # 5. Check US States & Cities (Cases 3, 5, 7)
        for state_name, sdata in self.us_state_by_name.items():
            # State name matching with word boundary
            state_pat = re.compile(rf'\b(?:residents\s+of\s+{state_name}|living\s+in\s+{state_name}|{state_name}\s+residents|participants\s+from\s+{state_name}|in\s+{state_name})\b', re.IGNORECASE)
            if state_pat.search(participant_context) or (re.search(rf'\b{state_name}\b', participant_context, re.IGNORECASE) and 'university' not in state_name):
                is_us = True
                matches.append(GeoMatch(country='US', state_province=sdata['name'], state_code=sdata['code'], scope=GeographyScope.STATE, confidence=0.95, match_text=sdata['name']))

            # State abbreviation pattern, e.g. "Phoenix, AZ" or "Dallas, TX" or "CA residents"
            code = sdata['code']
            code_pat = re.compile(rf'\b{code}\s+residents\b|,\s*{code}\b', re.IGNORECASE)
            if code_pat.search(participant_context):
                is_us = True
                matches.append(GeoMatch(country='US', state_province=sdata['name'], state_code=sdata['code'], scope=GeographyScope.STATE, confidence=0.92, match_text=code))

            # Major cities in this US state
            for city in sdata.get('cities', []):
                city_pat = re.compile(rf'\b(?:in\s+{city}|{city}\s+residents|participants\s+(?:needed\s+in|from)\s+{city}|living\s+in\s+{city}|{city}\s+metro|greater\s+{city})\b', re.IGNORECASE)
                if city_pat.search(participant_context):
                    is_us = True
                    matches.append(GeoMatch(country='US', state_province=sdata['name'], state_code=sdata['code'], city=city, scope=GeographyScope.CITY, confidence=0.96, match_text=city))

            # Regions & Counties
            for reg in sdata.get('regions', []):
                if re.search(rf'\b{re.escape(reg)}\b', participant_context, re.IGNORECASE):
                    is_us = True
                    matches.append(GeoMatch(country='US', state_province=sdata['name'], scope=GeographyScope.REGION, confidence=0.93, match_text=reg))

        # 6. Check Canadian Provinces & Cities (Cases 4, 6, 8)
        for prov_name, pdata in self.ca_prov_by_name.items():
            prov_pat = re.compile(rf'\b(?:residents\s+of\s+{prov_name}|living\s+in\s+{prov_name}|{prov_name}\s+residents|participants\s+from\s+{prov_name}|in\s+{prov_name})\b', re.IGNORECASE)
            if prov_pat.search(participant_context) or re.search(rf'\b{prov_name}\b', participant_context, re.IGNORECASE):
                is_ca = True
                scope_type = GeographyScope.TERRITORY if pdata['code'] in ('NT', 'NU', 'YT') else GeographyScope.PROVINCE
                matches.append(GeoMatch(country='CA', state_province=pdata['name'], state_code=pdata['code'], scope=scope_type, confidence=0.95, match_text=pdata['name']))

            code = pdata['code']
            code_pat = re.compile(rf'\b{code}\s+residents\b|,\s*{code}\b', re.IGNORECASE)
            if code_pat.search(participant_context):
                is_ca = True
                matches.append(GeoMatch(country='CA', state_province=pdata['name'], state_code=pdata['code'], scope=GeographyScope.PROVINCE, confidence=0.92, match_text=code))

            for city in pdata.get('cities', []):
                city_pat = re.compile(rf'\b(?:in\s+{city}|{city}\s+residents|participants\s+(?:needed\s+in|from)\s+{city}|living\s+in\s+{city}|greater\s+{city}\s+area|{city}\s+area)\b', re.IGNORECASE)
                if city_pat.search(participant_context):
                    is_ca = True
                    matches.append(GeoMatch(country='CA', state_province=pdata['name'], state_code=pdata['code'], city=city, scope=GeographyScope.CITY, confidence=0.96, match_text=city))

        # 7. Check North America / Worldwide explicit inclusion (Cases 10, 11)
        na_pattern = re.compile(r'\bnorth\s+america\b', re.IGNORECASE)
        global_pattern = re.compile(r'\b(?:worldwide|global|international)\b', re.IGNORECASE)
        has_na = bool(na_pattern.search(participant_context))
        has_global = bool(global_pattern.search(participant_context))

        if (has_na or has_global) and (is_us or is_ca):
            pass  # Already marked eligible
        elif (has_na or has_global) and not (is_us or is_ca):
            # Case 15 / Case 11 condition: Global without explicit US/CA eligibility does NOT qualify
            return GeographicResolutionResult(
                geography_status=GeographyStatus.UNKNOWN,
                participant_geo_confidence=0.40,
                matches=[],
                participant_locations=[],
                researcher_locations=[],
                is_eligible_us_or_ca=False,
                case_reason="Case 11/15: Global/remote without explicit US or Canada participant eligibility"
            )

        # 8. Check Case 12: "Remote" only without participant geography
        remote_only_pattern = re.compile(r'\b(?:remote|online|virtual|work\s+from\s+home)\b', re.IGNORECASE)
        if remote_only_pattern.search(participant_context) and not (is_us or is_ca):
            return GeographicResolutionResult(
                geography_status=GeographyStatus.UNKNOWN,
                participant_geo_confidence=0.30,
                matches=[GeoMatch(country='UNKNOWN', scope=GeographyScope.REMOTE, confidence=0.30, match_text='Remote without geography')],
                participant_locations=[],
                researcher_locations=[],
                is_eligible_us_or_ca=False,
                case_reason="Case 12: Opportunity is remote without identifying US/Canada participant geography"
            )

        # 9. Check Case 13: Researcher location in US/CA but participant location unknown or abroad
        if not is_us and not is_ca:
            # If US/CA appeared only in researcher context
            if self._has_us_or_ca_location(researcher_context):
                return GeographicResolutionResult(
                    geography_status=GeographyStatus.UNKNOWN,
                    participant_geo_confidence=0.35,
                    matches=[],
                    participant_locations=[],
                    researcher_locations=['US/Canada Researcher only'],
                    is_eligible_us_or_ca=False,
                    case_reason="Case 13: Organization is located in US/Canada but participant geography is unknown or outside target"
                )
            # Case 15: Geography is completely unknown
            return GeographicResolutionResult(
                geography_status=GeographyStatus.UNKNOWN,
                participant_geo_confidence=0.0,
                matches=[],
                participant_locations=[],
                researcher_locations=[],
                is_eligible_us_or_ca=False,
                case_reason="Case 15: Geographic eligibility unknown"
            )

        # Determine combined status
        if is_us and is_ca:
            status = GeographyStatus.US_CA_ELIGIBLE
            case_reason = "Case 9: Targets both United States and Canada"
        elif is_us:
            status = GeographyStatus.US_ELIGIBLE
            case_reason = "Case 1/3/5/7: Targets United States participants"
        else:
            status = GeographyStatus.CA_ELIGIBLE
            case_reason = "Case 2/4/6/8: Targets Canadian participants"

        # Check multi-state / multi-province
        us_states_found = {m.state_code for m in matches if m.country == 'US' and m.state_code}
        ca_provs_found = {m.state_code for m in matches if m.country == 'CA' and m.state_code}
        if len(us_states_found) > 1:
            matches.append(GeoMatch(country='US', scope=GeographyScope.MULTI_STATE, confidence=0.95, match_text=f"Multi-State: {','.join(us_states_found)}"))
        if len(ca_provs_found) > 1:
            matches.append(GeoMatch(country='CA', scope=GeographyScope.MULTI_PROVINCE, confidence=0.95, match_text=f"Multi-Province: {','.join(ca_provs_found)}"))

        avg_conf = sum(m.confidence for m in matches) / len(matches) if matches else 0.90

        return GeographicResolutionResult(
            geography_status=status,
            participant_geo_confidence=min(1.0, avg_conf),
            matches=matches,
            participant_locations=[m.match_text for m in matches],
            researcher_locations=[],
            is_eligible_us_or_ca=True,
            case_reason=case_reason
        )

    def _split_participant_and_researcher_contexts(self, text: str) -> tuple[str, str]:
        """
        Splits text into participant-eligibility focused context vs researcher institution context.
        Explicitly removes researcher institution names from participant context so universities
        (e.g., University of Michigan, University of Toronto) are not mistaken for participant location requirements.
        """
        researcher_patterns = [
            re.compile(r'\b(?:conducted\s+by\s+researchers\s+at|conducted\s+by|hosted\s+by|researchers\s+at)\s+[^.,;\n]+', re.IGNORECASE),
            re.compile(r'\b(?:department\s+of\s+[^.,;\n]+at\s+[^.,;\n]+)', re.IGNORECASE),
            re.compile(r'\b(?:university\s+of\s+[A-Za-z]+|[A-Za-z]+\s+state\s+university|[A-Za-z]+\s+university)', re.IGNORECASE),
        ]

        researcher_cues = []
        cleaned_participant_text = text

        # Check for explicit eligibility section first
        eligibility_split = re.split(r'(?:eligibility|requirements|who\s+can\s+participate|looking\s+for|criteria)\s*:\s*', text, flags=re.IGNORECASE)
        if len(eligibility_split) > 1:
            participant_context = " ".join(eligibility_split[1:])
            researcher_context = eligibility_split[0]
            # Strip institution phrases from participant context if any leaked in
            for pat in researcher_patterns:
                participant_context = pat.sub(' ', participant_context)
            return participant_context, researcher_context

        # Strip all researcher phrases from text to form participant context
        for pat in researcher_patterns:
            matches = pat.findall(cleaned_participant_text)
            if matches:
                researcher_cues.extend(matches)
                cleaned_participant_text = pat.sub(' ', cleaned_participant_text)

        researcher_context = " ".join(researcher_cues)
        return cleaned_participant_text, researcher_context

    def _is_strictly_foreign(self, text: str) -> bool:
        for country in self.excluded_countries:
            pat = re.compile(rf'\b(?:{country}\s+only|residents\s+of\s+{country}\s+only|living\s+in\s+{country}\s+only|open\s+only\s+to\s+{country})\b', re.IGNORECASE)
            if pat.search(text):
                return True
        return False

    def _has_us_or_ca_location(self, text: str) -> bool:
        if not text:
            return False
        for s in self.gazetteer['us_states']:
            if s['name'].lower() in text.lower():
                return True
        for p in self.gazetteer['ca_provinces']:
            if p['name'].lower() in text.lower():
                return True
        return False
