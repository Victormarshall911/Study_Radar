'use client';

import React, { useState } from 'react';
import { Database, Play, Power, CheckCircle, AlertTriangle, Clock, RefreshCw, ExternalLink } from 'lucide-react';
import { Source, SourceRun } from '../types';
import { toggleSourceActive, triggerSourceRun } from '../services/api';

interface SourcesViewProps {
  sources: Source[];
  runs: SourceRun[];
  onRefresh: () => void;
  isLoading: boolean;
}

export const SourcesView: React.FC<SourcesViewProps> = ({ sources, runs, onRefresh, isLoading }) => {
  const [triggeringId, setTriggeringId] = useState<string | null>(null);
  const [togglingId, setTogglingId] = useState<string | null>(null);

  const handleToggle = async (id: string) => {
    try {
      setTogglingId(id);
      await toggleSourceActive(id);
      onRefresh();
    } catch (err: any) {
      alert(`Error toggling source: ${err.message}`);
    } finally {
      setTogglingId(null);
    }
  };

  const handleTrigger = async (id: string) => {
    try {
      setTriggeringId(id);
      await triggerSourceRun(id);
      alert('Discovery crawl task dispatched to Celery background worker!');
      onRefresh();
    } catch (err: any) {
      alert(`Error triggering crawl: ${err.message}`);
    } finally {
      setTriggeringId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <Database className="w-5 h-5 text-cyan-400" />
            <span>Permitted Discovery Connectors & Crawlers</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Ethical, rate-limited aggregation from official RSS feeds, APIs, and authorized university portals.
          </p>
        </div>

        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Status</span>
        </button>
      </div>

      {/* Sources Grid / Table */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sources.map((source) => (
          <div
            key={source.id}
            className={`p-5 rounded-2xl border transition-all ${
              source.is_active
                ? 'bg-slate-900/80 border-slate-800 shadow-xl'
                : 'bg-slate-950/60 border-slate-900 opacity-60'
            }`}
          >
            <div className="flex items-start justify-between gap-3 mb-3">
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="text-base font-bold text-white">{source.name}</h3>
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase ${
                      source.is_active
                        ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                        : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}
                  >
                    {source.is_active ? 'Active' : 'Disabled'}
                  </span>
                </div>
                <span className="text-[11px] text-cyan-400 font-mono block mt-0.5">
                  Type: {source.source_type.toUpperCase()}
                </span>
              </div>

              {/* Toggle and Trigger Buttons */}
              <div className="flex items-center space-x-1.5">
                <button
                  onClick={() => handleToggle(source.id)}
                  disabled={togglingId === source.id}
                  title={source.is_active ? 'Disable Source' : 'Enable Source'}
                  className={`p-2 rounded-xl border transition ${
                    source.is_active
                      ? 'bg-slate-800 hover:bg-red-500/20 text-slate-300 hover:text-red-400 border-slate-700'
                      : 'bg-emerald-950/60 hover:bg-emerald-900 text-emerald-400 border-emerald-800'
                  }`}
                >
                  <Power className="w-4 h-4" />
                </button>

                <button
                  onClick={() => handleTrigger(source.id)}
                  disabled={triggeringId === source.id || !source.is_active}
                  className="flex items-center space-x-1 px-3 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 text-white text-xs font-semibold shadow transition"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>{triggeringId === source.id ? 'Running...' : 'Run Now'}</span>
                </button>
              </div>
            </div>

            <p className="text-xs text-slate-400 mb-4 line-clamp-2">
              {source.compliance_notes || 'Permitted discovery connector.'}
            </p>

            {/* Metrics Footer */}
            <div className="grid grid-cols-3 gap-2 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
              <div>
                <span className="block text-[10px] text-slate-500">Interval</span>
                <span className="font-semibold text-slate-300">{source.crawl_interval_seconds / 60} mins</span>
              </div>

              <div>
                <span className="block text-[10px] text-slate-500">Rate Limit</span>
                <span className="font-semibold text-slate-300">{source.rate_limit_rps} req/s</span>
              </div>

              <div>
                <span className="block text-[10px] text-slate-500">Last Crawled</span>
                <span className="font-semibold text-slate-300">
                  {source.last_run_at
                    ? new Date(source.last_run_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    : 'Pending'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Crawl Run Execution Logs */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-2">
          <Clock className="w-4 h-4 text-cyan-400" />
          <span>Recent Discovery Run Executions</span>
        </h3>

        {runs.length === 0 ? (
          <p className="text-xs text-slate-500 py-4 text-center">No background crawl runs recorded yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Source</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Fetched</th>
                  <th className="py-2.5 px-3">Accepted</th>
                  <th className="py-2.5 px-3">Duplicates</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {runs.slice(0, 8).map((run) => (
                  <tr key={run.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 font-medium text-white">{run.source_name}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          run.status === 'success'
                            ? 'bg-emerald-500/15 text-emerald-400'
                            : 'bg-red-500/15 text-red-400'
                        }`}
                      >
                        {run.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">{run.items_fetched}</td>
                    <td className="py-2.5 px-3 text-emerald-400 font-semibold">{run.items_accepted}</td>
                    <td className="py-2.5 px-3 text-purple-400">{run.duplicate_count}</td>
                    <td className="py-2.5 px-3 text-slate-400">
                      {new Date(run.started_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
