'use client';

import React, { useState } from 'react';
import { Search, Activity, ShieldCheck, CheckCircle2, XCircle, AlertCircle, Save, ExternalLink } from 'lucide-react';
import { ManualIngestResult } from '../types';
import { runManualIngestion } from '../services/api';

export const ManualIngestionTool: React.FC = () => {
  const [url, setUrl] = useState('');
  const [saveToDb, setSaveToDb] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ManualIngestResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleInspect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await runManualIngestion(url.trim(), saveToDb);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Inspection failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white flex items-center space-x-2">
          <Activity className="w-5 h-5 text-cyan-400" />
          <span>Real-Time URL Ingestion & Pipeline Inspector</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Paste any public URL to execute the 7-step Study Radar inspection pipeline (SSRF Safety, Classification, Date, Geography, 7-Day Freshness, and Qualification).
        </p>
      </div>

      {/* Ingestion Form */}
      <form onSubmit={handleInspect} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
            Opportunity Target URL
          </label>
          <div className="flex gap-3">
            <input
              type="url"
              required
              placeholder="https://dsl.harvard.edu/participate or https://..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex-1 px-4 py-2.5 text-sm bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 text-white text-xs font-bold shadow-lg shadow-cyan-500/20 transition flex items-center space-x-2"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Inspecting...</span>
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  <span>Inspect URL</span>
                </>
              )}
            </button>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="saveToDb"
            checked={saveToDb}
            onChange={(e) => setSaveToDb(e.target.checked)}
            className="w-4 h-4 text-cyan-500 rounded bg-slate-950 border-slate-800 focus:ring-cyan-500"
          />
          <label htmlFor="saveToDb" className="text-xs text-slate-400 cursor-pointer">
            Save candidate to database and apply deduplication if qualifying
          </label>
        </div>
      </form>

      {/* Error Message */}
      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-xs text-red-300 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Inspection Pipeline Results */}
      {result && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-6 animate-in fade-in">
          {/* Top Banner: Final Qualification Decision */}
          <div
            className={`p-4 rounded-xl border flex items-center justify-between ${
              result.qualifies_for_alert
                ? 'bg-emerald-950/50 border-emerald-500/40 text-emerald-300'
                : 'bg-amber-950/40 border-amber-500/40 text-amber-300'
            }`}
          >
            <div className="flex items-center space-x-3">
              {result.qualifies_for_alert ? (
                <CheckCircle2 className="w-6 h-6 text-emerald-400" />
              ) : (
                <XCircle className="w-6 h-6 text-amber-400" />
              )}
              <div>
                <h4 className="text-sm font-bold">
                  {result.qualifies_for_alert
                    ? 'QUALIFIES FOR 7-DAY US/CA RESEARCH ALERT'
                    : 'DOES NOT QUALIFY FOR ALERT'}
                </h4>
                <p className="text-xs opacity-90 mt-0.5">
                  {result.qualifies_for_alert
                    ? 'Meets all 3 mandatory criteria (Research study + Published within 7 days + US/CA eligible).'
                    : `Reason: ${result.exclusion_reason || result.geographic_reason}`}
                </p>
              </div>
            </div>

            {result.saved_opportunity_id && (
              <span className="text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
                Saved (ID: {result.saved_opportunity_id.slice(0, 8)})
              </span>
            )}
          </div>

          {/* 7-Step Inspection Pipeline Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Step 1 & 2: Crawl & Sanitization */}
            <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800 space-y-2">
              <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">
                1. Crawl & Security
              </span>
              <p className="text-xs font-semibold text-white truncate">{result.title}</p>
              <div className="text-[11px] text-slate-400 space-y-1">
                <p>Status: HTTP {result.status_code} OK (SSRF Check Passed)</p>
                <p>Canonical: {result.canonical_url}</p>
                {result.organization && <p>Organization: {result.organization}</p>}
              </div>
            </div>

            {/* Step 3: Classifier */}
            <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800 space-y-2">
              <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">
                2. Classification & Reward
              </span>
              <p className="text-xs font-semibold text-white">
                {result.is_research_opportunity ? 'Valid Research Opportunity' : 'Non-Research Opportunity'}
              </p>
              <div className="text-[11px] text-slate-400 space-y-1">
                <p>Type: {result.study_type}</p>
                <p>Reward: {result.reward || 'Unspecified'}</p>
                <p>Duration: {result.duration || 'Unspecified'}</p>
              </div>
            </div>

            {/* Step 4: Publication Date */}
            <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800 space-y-2">
              <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">
                3. Date Extraction & Freshness
              </span>
              <p className="text-xs font-semibold text-white">
                {result.is_fresh_7_days ? 'Fresh (<= 7 Days)' : 'Expired / Stale (> 7 Days)'}
              </p>
              <div className="text-[11px] text-slate-400 space-y-1">
                <p>Published: {result.published_at ? new Date(result.published_at).toLocaleString() : 'Unknown'}</p>
                <p>Age: {result.days_old !== undefined ? `${result.days_old} days ago` : 'Unknown'}</p>
                <p>Source: {result.date_source} ({Math.round(result.date_confidence * 100)}% conf)</p>
              </div>
            </div>

            {/* Step 5: Geography */}
            <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800 space-y-2">
              <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">
                4. Geographic Target (US/Canada)
              </span>
              <p className="text-xs font-semibold text-white">
                Status: {result.geography_status.toUpperCase()}
              </p>
              <div className="text-[11px] text-slate-400 space-y-1">
                <p>Confidence: {Math.round(result.geography_confidence * 100)}%</p>
                <p>Decision: {result.geographic_reason}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
