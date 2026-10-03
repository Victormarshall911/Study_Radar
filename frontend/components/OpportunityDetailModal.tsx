'use client';

import React from 'react';
import { X, MapPin, Building2, Calendar, DollarSign, Clock, ShieldCheck, ExternalLink, Globe, Layers, Bell } from 'lucide-react';
import { Opportunity } from '../types';

interface OpportunityDetailModalProps {
  opportunity: Opportunity | null;
  onClose: () => void;
  onTriggerNotification?: (id: string) => void;
}

export const OpportunityDetailModal: React.FC<OpportunityDetailModalProps> = ({
  opportunity,
  onClose,
  onTriggerNotification,
}) => {
  if (!opportunity) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl p-6 sm:p-8 space-y-6">
        {/* Header & Close Button */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                {opportunity.is_fresh ? 'Fresh within 7 Days' : 'Archived (> 7 Days)'}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
                {opportunity.study_type.replace('_', ' ').toUpperCase()}
              </span>
              {opportunity.has_been_notified && (
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-500/15 text-purple-400 border border-purple-500/30 flex items-center space-x-1">
                  <Bell className="w-3 h-3" />
                  <span>Alert Sent</span>
                </span>
              )}
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white leading-tight">
              {opportunity.title}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-xl bg-slate-800/80 hover:bg-slate-700 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Quick Highlights Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-2xl bg-slate-950/60 border border-slate-800">
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 flex items-center space-x-1">
              <DollarSign className="w-3 h-3 text-emerald-400" />
              <span>Reward</span>
            </span>
            <p className="text-sm font-semibold text-emerald-400 mt-1">
              {opportunity.reward_text || (opportunity.reward_amount ? `$${opportunity.reward_amount}` : 'Unpaid')}
            </p>
          </div>

          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 flex items-center space-x-1">
              <Clock className="w-3 h-3 text-cyan-400" />
              <span>Duration</span>
            </span>
            <p className="text-sm font-semibold text-slate-200 mt-1">
              {opportunity.duration_text || (opportunity.duration_minutes ? `${opportunity.duration_minutes} mins` : 'Flexible')}
            </p>
          </div>

          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 flex items-center space-x-1">
              <Calendar className="w-3 h-3 text-blue-400" />
              <span>Published At</span>
            </span>
            <p className="text-xs font-semibold text-slate-200 mt-1">
              {opportunity.published_at
                ? new Date(opportunity.published_at).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })
                : 'Unknown'}
            </p>
          </div>

          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 flex items-center space-x-1">
              <ShieldCheck className="w-3 h-3 text-amber-400" />
              <span>Confidence</span>
            </span>
            <p className="text-xs font-semibold text-slate-200 mt-1">
              Date: {Math.round(opportunity.date_confidence * 100)}% | Geo: {Math.round(opportunity.participant_geo_confidence * 100)}%
            </p>
          </div>
        </div>

        {/* Participant Geography vs Researcher Organization */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800 space-y-2">
            <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center space-x-1.5">
              <MapPin className="w-4 h-4" />
              <span>Participant Eligibility Geography</span>
            </h4>
            <div className="text-sm text-slate-200">
              {opportunity.geographies && opportunity.geographies.length > 0 ? (
                <ul className="list-disc list-inside space-y-1 text-xs">
                  {opportunity.geographies.map((g, i) => (
                    <li key={i}>
                      {g.geography.city ? `${g.geography.city}, ` : ''}
                      {g.geography.state_province || g.geography.country} ({g.scope})
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-slate-400">
                  Target: {opportunity.geography_status === 'us_eligible' ? 'United States' : opportunity.geography_status === 'ca_eligible' ? 'Canada' : 'US & Canada'}
                </p>
              )}
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800 space-y-2">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
              <Building2 className="w-4 h-4" />
              <span>Researcher Organization</span>
            </h4>
            <p className="text-sm font-semibold text-slate-200">
              {opportunity.organization || 'Public Research Institution'}
            </p>
            {opportunity.researcher_location && (
              <p className="text-xs text-slate-400">
                Institution Location: {opportunity.researcher_location}
              </p>
            )}
          </div>
        </div>

        {/* Eligibility Requirements */}
        {opportunity.eligibility_text && (
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Participant Criteria & Requirements
            </h4>
            <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300 leading-relaxed">
              {opportunity.eligibility_text}
            </div>
          </div>
        )}

        {/* Study Description */}
        {opportunity.description && (
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Study Overview
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed max-h-40 overflow-y-auto">
              {opportunity.description}
            </p>
          </div>
        )}

        {/* Multi-Source Deduplication Sightings */}
        {opportunity.sources && opportunity.sources.length > 0 && (
          <div className="space-y-2 pt-2 border-t border-slate-800">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
              <Layers className="w-4 h-4 text-purple-400" />
              <span>Discovery Sources & Sightings ({opportunity.sources.length})</span>
            </h4>
            <div className="space-y-1 text-xs">
              {opportunity.sources.map((s, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-slate-950/40 border border-slate-800/80">
                  <span className="font-medium text-slate-300">{s.source_name} ({s.source_type})</span>
                  <a
                    href={s.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-cyan-400 hover:underline flex items-center space-x-1"
                  >
                    <span>Source Link</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-slate-800">
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <span>Canonical ID:</span>
            <span className="font-mono text-slate-300">{opportunity.id.slice(0, 8)}</span>
          </div>

          <div className="flex items-center space-x-3 w-full sm:w-auto">
            {onTriggerNotification && (
              <button
                onClick={() => onTriggerNotification(opportunity.id)}
                className="flex-1 sm:flex-none px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
              >
                Send Alert Now
              </button>
            )}

            <a
              href={opportunity.application_url || opportunity.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-bold shadow-lg shadow-cyan-500/20 flex items-center justify-center space-x-2 transition"
            >
              <span>Apply for Study</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
