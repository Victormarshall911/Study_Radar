import { DashboardMetrics, Opportunity, Source, SourceRun, ManualIngestResult } from '../types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8008/api';

export async function fetchMetrics(): Promise<DashboardMetrics> {
  const res = await fetch(`${API_BASE}/stats/`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch stats: ${res.statusText}`);
  return res.json();
}

export async function fetchOpportunities(params: Record<string, string> = {}): Promise<{ results: Opportunity[]; count: number }> {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value) searchParams.append(key, value);
  }
  const url = `${API_BASE}/opportunities/?${searchParams.toString()}`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch opportunities: ${res.statusText}`);
  const data = await res.json();
  if (Array.isArray(data)) {
    return { results: data, count: data.length };
  }
  return { results: data.results || [], count: data.count || 0 };
}

export async function fetchOpportunityDetail(id: string): Promise<Opportunity> {
  const res = await fetch(`${API_BASE}/opportunities/${id}/`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch opportunity: ${res.statusText}`);
  return res.json();
}

export async function fetchSources(): Promise<Source[]> {
  const res = await fetch(`${API_BASE}/sources/`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch sources: ${res.statusText}`);
  const data = await res.json();
  return Array.isArray(data) ? data : data.results || [];
}

export async function fetchSourceRuns(): Promise<SourceRun[]> {
  const res = await fetch(`${API_BASE}/sources/runs/`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch source runs: ${res.statusText}`);
  const data = await res.json();
  return Array.isArray(data) ? data : data.results || [];
}

export async function toggleSourceActive(id: string): Promise<{ id: string; is_active: boolean }> {
  const res = await fetch(`${API_BASE}/sources/${id}/toggle_active/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  if (!res.ok) throw new Error(`Failed to toggle source: ${res.statusText}`);
  return res.json();
}

export async function triggerSourceRun(id: string): Promise<any> {
  const res = await fetch(`${API_BASE}/sources/${id}/trigger_run/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  if (!res.ok) throw new Error(`Failed to trigger source run: ${res.statusText}`);
  return res.json();
}

export async function runManualIngestion(url: string, saveToDb: boolean = false): Promise<ManualIngestResult> {
  const res = await fetch(`${API_BASE}/ingest/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, save_to_database: saveToDb })
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.error || `Ingestion failed (${res.status})`);
  }
  return res.json();
}

export async function testNotification(channel: string = 'local_log'): Promise<any> {
  const res = await fetch(`${API_BASE}/notifications/test/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ channel, timestamp: new Date().toISOString() })
  });
  if (!res.ok) throw new Error(`Failed to test notification: ${res.statusText}`);
  return res.json();
}
