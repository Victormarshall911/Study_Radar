'use client';

import React from 'react';
import { Sparkles, Clock, Globe2, DollarSign, Database, CheckCircle2, ShieldCheck, Layers } from 'lucide-react';
import { DashboardMetrics } from '../types';

interface MetricCardsProps {
  metrics: DashboardMetrics | null;
  isLoading: boolean;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ metrics, isLoading }) => {
  const cards = [
    {
      title: 'New in 24h',
      value: metrics?.new_24h ?? 0,
      icon: Sparkles,
      color: 'from-amber-500/20 to-amber-600/10 border-amber-500/30 text-amber-400',
      badge: 'Immediate',
    },
    {
      title: 'New in 7 Days',
      value: metrics?.new_7d ?? 0,
      icon: Clock,
      color: 'from-emerald-500/20 to-emerald-600/10 border-emerald-500/30 text-emerald-400',
      badge: 'Freshness Window',
    },
    {
      title: 'United States',
      value: metrics?.us_opportunities ?? 0,
      icon: Globe2,
      color: 'from-blue-500/20 to-blue-600/10 border-blue-500/30 text-blue-400',
      badge: '50 States + DC',
    },
    {
      title: 'Canada',
      value: metrics?.canada_opportunities ?? 0,
      icon: Globe2,
      color: 'from-red-500/20 to-red-600/10 border-red-500/30 text-red-400',
      badge: 'Provinces & Terr.',
    },
    {
      title: 'Paid Studies',
      value: metrics?.paid_opportunities ?? 0,
      icon: DollarSign,
      color: 'from-cyan-500/20 to-cyan-600/10 border-cyan-500/30 text-cyan-400',
      badge: 'Compensated',
    },
    {
      title: 'Duplicates Filtered',
      value: metrics?.duplicates_removed ?? 0,
      icon: Layers,
      color: 'from-purple-500/20 to-purple-600/10 border-purple-500/30 text-purple-400',
      badge: 'De-duplicated',
    },
    {
      title: 'Sources Active',
      value: metrics?.sources_monitored ?? 0,
      icon: Database,
      color: 'from-slate-800 to-slate-900 border-slate-700 text-slate-300',
      badge: 'Monitored',
    },
    {
      title: 'Crawl Runs Ok',
      value: metrics?.successful_source_runs ?? 0,
      icon: CheckCircle2,
      color: 'from-slate-800 to-slate-900 border-slate-700 text-slate-300',
      badge: 'Health',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`p-3.5 rounded-xl bg-gradient-to-br ${card.color} border transition-all hover:scale-[1.02] flex flex-col justify-between`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-medium text-slate-400 uppercase tracking-wider truncate">
                {card.title}
              </span>
              <Icon className="w-3.5 h-3.5 opacity-80" />
            </div>
            <div>
              <div className="text-xl sm:text-2xl font-bold tracking-tight text-white">
                {isLoading ? (
                  <span className="inline-block w-8 h-6 bg-slate-700/50 animate-pulse rounded"></span>
                ) : (
                  card.value
                )}
              </div>
              <span className="text-[9px] text-slate-400 block truncate mt-0.5">
                {card.badge}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
