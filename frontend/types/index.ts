export interface Geography {
  id: string;
  country: string;
  state_province?: string;
  state_code?: string;
  city?: string;
  county?: string;
  metro_area?: string;
  region?: string;
  scope: string;
  is_us: boolean;
  is_ca: boolean;
}

export interface OpportunityGeography {
  id: string;
  geography: Geography;
  scope: string;
  is_explicit: boolean;
  confidence: number;
}

export interface OpportunitySource {
  id: string;
  source: string;
  source_name: string;
  source_type: string;
  source_url: string;
  discovered_at: string;
}

export interface Opportunity {
  id: string;
  title: string;
  description?: string;
  study_type: string;
  organization?: string;
  researcher_location?: string;
  source_url: string;
  canonical_url?: string;
  application_url?: string;
  published_at?: string;
  published_at_timezone?: string;
  published_date_precision?: string;
  date_confidence: number;
  reward_amount?: number;
  reward_currency?: string;
  reward_text?: string;
  reward_type?: string;
  is_paid: boolean;
  duration_minutes?: number;
  duration_text?: string;
  eligibility_text?: string;
  geography_status: 'us_eligible' | 'ca_eligible' | 'us_ca_eligible' | 'outside_target' | 'unknown';
  participant_geo_confidence: number;
  status: string;
  exclusion_reason?: string;
  has_been_notified: boolean;
  discovered_at: string;
  geographies: OpportunityGeography[];
  sources?: OpportunitySource[];
  is_fresh: boolean;
  is_eligible_for_alert: boolean;
  duplicate_count?: number;
  repost_detected?: boolean;
}

export interface DashboardMetrics {
  new_24h: number;
  new_7d: number;
  us_opportunities: number;
  canada_opportunities: number;
  paid_opportunities: number;
  unpaid_opportunities: number;
  sources_monitored: number;
  successful_source_runs: number;
  failed_source_runs: number;
  duplicates_removed: number;
  total_discovered: number;
  server_time: string;
}

export interface Source {
  id: string;
  name: string;
  slug: string;
  source_type: string;
  base_url: string;
  feed_or_api_url?: string;
  is_active: boolean;
  crawl_interval_seconds: number;
  rate_limit_rps: number;
  compliance_notes: string;
  last_run_at?: string;
  last_success_at?: string;
  failure_count: number;
  avg_response_time_ms: number;
  status: 'idle' | 'running' | 'failing' | 'disabled';
  run_count?: number;
}

export interface SourceRun {
  id: string;
  source: string;
  source_name: string;
  started_at: string;
  finished_at?: string;
  status: 'running' | 'success' | 'failed' | 'partial';
  items_fetched: number;
  items_parsed: number;
  items_rejected: number;
  items_accepted: number;
  duplicate_count: number;
  error_message?: string;
  response_time_ms: number;
}

export interface ManualIngestResult {
  url: string;
  final_url: string;
  status_code: number;
  title: string;
  canonical_url: string;
  is_research_opportunity: boolean;
  study_type: string;
  reward?: string;
  duration?: string;
  eligibility?: string;
  organization?: string;
  published_at?: string;
  date_source?: string;
  date_precision?: string;
  date_confidence: number;
  days_old?: number;
  is_fresh_7_days: boolean;
  geography_status: string;
  geography_confidence: number;
  geography_matches: any[];
  geographic_reason: string;
  qualifies_for_alert: boolean;
  exclusion_reason?: string;
  saved_opportunity_id?: string;
  deduplication_result?: string;
}
