'use client';

import React from 'react';
import { MapPin, DollarSign, Clock, ExternalLink, Building2, ShieldCheck, Flame } from 'lucide-react';
import { Opportunity } from '../types';

interface OpportunityCardProps {
  opportunity: Opportunity;
  onSelect: (opp: Opportunity) => void;
}

export const OpportunityCard: React.FC<OpportunityCardProps> = ({ opportunity, onSelect }) => {
  // Format relative freshness string
  const formatFreshness = (publishedAt?: string) => {
    if (!publishedAt) return { text: 'Date Unknown', isHot: false };
    const diffMs = new Date().getTime() - new Date(publishedAt).getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return { text: 'NEW — Just now', isHot: true };
    if (diffHours < 24) return { text: `NEW — ${diffHours}h ago`, isHot: true };
    if (diffDays === 1) return { text: '1 day ago', isHot: true };
    if (diffDays <= 7) return { text: `${diffDays} days ago`, isHot: false };
    return { text: `${diffDays} days ago (Archived)`, isHot: false };
  };

  const freshness = formatFreshness(opportunity.published_at);

  // Geographic display string
  const locationDisplay = () => {
    const geos = opportunity.geographies || [];
    if (geos.length > 0) {
      const g = geos[0].geography;
      if (g.city && (g.state_code || g.state_province)) {
        return `${g.city}, ${g.state_code || g.state_province} (${g.country})`;
      }
      if (g.state_province) {
        return `${g.state_province}, ${g.country}`;
      }
      if (g.country) {
        return g.country === 'US' ? 'United States (Nationwide)' : 'Canada (Nationwide)';
      }
    }
    if (opportunity.geography_status === 'us_eligible') return 'United States';
    if (opportunity.geography_status === 'ca_eligible') return 'Canada';
    if (opportunity.geography_status === 'us_ca_eligible') return 'US & Canada';
    return 'Geography Specified';
  };

  const isCanada = opportunity.geography_status === 'ca_eligible';

  return (
    <div
      onClick={() => onSelect(opportunity)}
      className="group relative bg-slate-900/70 hover:bg-slate-900 border border-slate-800 hover:border-cyan-500/40 rounded-2xl p-5 shadow-lg transition-all duration-200 cursor-pointer flex flex-col justify-between"
    >
      <div>
        {/* Top Badges: Freshness, Region, and Type */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div className="flex items-center space-x-1.5">
            <span
              className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide ${
                freshness.isHot
                  ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                  : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
              }`}
            >
              {freshness.isHot && <Flame className="w-3 h-3 text-amber-400 animate-pulse" />}
              <span>{freshness.text}</span>
            </span>

            <span
              className={`px-2 py-0.5 rounded-full text-[11px] font-medium ${
                isCanada
                  ? 'bg-red-500/10 text-red-300 border border-red-500/20'
                  : 'bg-blue-500/10 text-blue-300 border border-blue-500/20'
              }`}
            >
              {isCanada ? '🇨🇦 Canada' : '🇺🇸 United States'}
            </span>
          </div>

          {/* Study Type */}
          <span className="text-[11px] px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 font-medium">
            {opportunity.study_type.replace('_', ' ').toUpperCase()}
          </span>
        </div>

        {/* Title */}
        <h3 className="text-base font-semibold text-white group-hover:text-cyan-400 transition-colors line-clamp-2 leading-snug mb-2">
          {opportunity.title}
        </h3>

        {/* Organization & Location */}
        <div className="space-y-1 mb-4 text-xs text-slate-400">
          <div className="flex items-center space-x-1.5">
            <MapPin className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <span className="truncate text-slate-300">{locationDisplay()}</span>
          </div>

          {opportunity.organization && (
            <div className="flex items-center space-x-1.5">
              <Building2 className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              <span className="truncate">{opportunity.organization}</span>
            </div>
          )}
        </div>

        {/* Eligibility Snippet */}
        {opportunity.eligibility_text && (
          <p className="text-xs text-slate-400 line-clamp-2 mb-4 bg-slate-950/40 p-2.5 rounded-xl border border-slate-800/60">
            <span className="font-semibold text-slate-300">Eligibility:</span> {opportunity.eligibility_text}
          </p>
        )}
      </div>

      {/* Bottom Bar: Reward, Duration, and Action */}
      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-3">
          {/* Reward */}
          <div className="flex items-center space-x-1 font-semibold text-emerald-400">
            <DollarSign className="w-3.5 h-3.5" />
            <span>
              {opportunity.reward_text ||
                (opportunity.reward_amount ? `$${opportunity.reward_amount}` : 'Unpaid')}
            </span>
          </div>

          {/* Duration */}
          {opportunity.duration_text && (
            <div className="flex items-center space-x-1 text-slate-400">
              <Clock className="w-3.5 h-3.5" />
              <span>{opportunity.duration_text}</span>
            </div>
          )}
        </div>

        {/* External Link */}
        <a
          href={opportunity.application_url || opportunity.source_url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="flex items-center space-x-1 text-cyan-400 hover:text-cyan-300 font-medium transition"
        >
          <span>Apply</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </div>
  );
};
