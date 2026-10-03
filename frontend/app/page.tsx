'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from '../components/Navbar';
import { MetricCards } from '../components/MetricCards';
import { FilterBar } from '../components/FilterBar';
import { OpportunityCard } from '../components/OpportunityCard';
import { OpportunityDetailModal } from '../components/OpportunityDetailModal';
import { SourcesView } from '../components/SourcesView';
import { ManualIngestionTool } from '../components/ManualIngestionTool';
import { Opportunity, DashboardMetrics, Source, SourceRun } from '../types';
import { fetchMetrics, fetchOpportunities, fetchSources, fetchSourceRuns, testNotification } from '../services/api';
import { Radar, RefreshCw, AlertCircle, Compass, Sparkles } from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'radar' | 'sources' | 'ingest' | 'analytics'>('radar');
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [runs, setSourceRuns] = useState<SourceRun[]>([]);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);

  const [isLoadingMetrics, setIsLoadingMetrics] = useState(false);
  const [isLoadingOpps, setIsLoadingOpps] = useState(false);
  const [isLoadingSources, setIsLoadingSources] = useState(false);
  const [isTestingAlert, setIsTestingAlert] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters state (Defaulting to 7-day freshness as required by instruction.md)
  const [filters, setFilters] = useState({
    country: '',
    state: '',
    city: '',
    study_type: '',
    paid: '',
    posted_within: '7d',
    search: '',
  });

  const loadMetrics = useCallback(async () => {
    try {
      setIsLoadingMetrics(true);
      const data = await fetchMetrics();
      setMetrics(data);
    } catch (err: any) {
      console.error('Error fetching metrics:', err);
    } finally {
      setIsLoadingMetrics(false);
    }
  }, []);

  const loadOpportunities = useCallback(async () => {
    try {
      setIsLoadingOpps(true);
      setError(null);
      const data = await fetchOpportunities(filters);
      setOpportunities(data.results);
    } catch (err: any) {
      setError('Could not connect to backend API server. Make sure the backend is running.');
      console.error('Error fetching opportunities:', err);
    } finally {
      setIsLoadingOpps(false);
    }
  }, [filters]);

  const loadSourcesData = useCallback(async () => {
    try {
      setIsLoadingSources(true);
      const [srcData, runData] = await Promise.all([fetchSources(), fetchSourceRuns()]);
      setSources(srcData);
      setSourceRuns(runData);
    } catch (err: any) {
      console.error('Error fetching sources:', err);
    } finally {
      setIsLoadingSources(false);
    }
  }, []);

  useEffect(() => {
    loadMetrics();
    loadOpportunities();
    loadSourcesData();
  }, [loadMetrics, loadOpportunities, loadSourcesData]);

  const handleFilterChange = (key: keyof typeof filters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleResetFilters = () => {
    setFilters({
      country: '',
      state: '',
      city: '',
      study_type: '',
      paid: '',
      posted_within: '7d',
      search: '',
    });
  };

  const handleTestAlert = async () => {
    try {
      setIsTestingAlert(true);
      await testNotification('local_log');
      alert('Test alert dispatched to audit log successfully!');
    } catch (err: any) {
      alert(`Test alert error: ${err.message}`);
    } finally {
      setIsTestingAlert(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500 selection:text-white">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onTestNotification={handleTestAlert}
        isTestingNotification={isTestingAlert}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Metric Cards (Section 59) */}
        <MetricCards metrics={metrics} isLoading={isLoadingMetrics} />

        {/* Dynamic Tab Body */}
        {activeTab === 'radar' && (
          <div className="space-y-6">
            {/* Filter Bar */}
            <FilterBar
              filters={filters}
              onChange={handleFilterChange}
              onReset={handleResetFilters}
            />

            {/* Error Notification */}
            {error && (
              <div className="p-4 rounded-2xl bg-amber-950/40 border border-amber-800 text-xs text-amber-300 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>{error}</span>
                </div>
                <button
                  onClick={loadOpportunities}
                  className="px-3 py-1 bg-amber-900/60 hover:bg-amber-800 text-amber-200 rounded-lg font-medium"
                >
                  Retry
                </button>
              </div>
            )}

            {/* Opportunities Feed Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center space-x-2">
                  <Compass className="w-5 h-5 text-cyan-400" />
                  <span>Discovered Participant Opportunities</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-normal">
                    {opportunities.length}
                  </span>
                </h2>
                <p className="text-xs text-slate-400">
                  Strictly filtering research studies posted within the last 7 days for US and Canada.
                </p>
              </div>

              <button
                onClick={loadOpportunities}
                disabled={isLoadingOpps}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isLoadingOpps ? 'animate-spin' : ''}`} />
                <span>Refresh Feed</span>
              </button>
            </div>

            {/* Opportunities Cards Grid */}
            {isLoadingOpps ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="h-48 rounded-2xl bg-slate-900/50 border border-slate-800 animate-pulse p-5">
                    <div className="h-4 bg-slate-800 rounded w-1/3 mb-4"></div>
                    <div className="h-6 bg-slate-800 rounded w-3/4 mb-4"></div>
                    <div className="h-4 bg-slate-800 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : opportunities.length === 0 ? (
              <div className="text-center py-16 px-4 rounded-3xl bg-slate-900/40 border border-slate-800/80 space-y-3">
                <Radar className="w-12 h-12 text-slate-600 mx-auto" />
                <h3 className="text-base font-semibold text-slate-300">No matching studies found</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  Try adjusting your state/city filter or expanding the freshness window.
                </p>
                <button
                  onClick={handleResetFilters}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white transition"
                >
                  Reset All Filters
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {opportunities.map((opp) => (
                  <OpportunityCard
                    key={opp.id}
                    opportunity={opp}
                    onSelect={(selected) => setSelectedOpportunity(selected)}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Sources Management Tab */}
        {activeTab === 'sources' && (
          <SourcesView
            sources={sources}
            runs={runs}
            onRefresh={loadSourcesData}
            isLoading={isLoadingSources}
          />
        )}

        {/* Real-Time Inspector & Manual Ingestion Tab */}
        {activeTab === 'ingest' && <ManualIngestionTool />}
      </main>

      {/* Detail Drilldown Modal */}
      <OpportunityDetailModal
        opportunity={selectedOpportunity}
        onClose={() => setSelectedOpportunity(null)}
      />
    </div>
  );
}
