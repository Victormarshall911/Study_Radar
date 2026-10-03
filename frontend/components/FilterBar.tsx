'use client';

import React from 'react';
import { Search, Filter, RotateCcw, MapPin, DollarSign, Clock } from 'lucide-react';

interface FilterState {
  country: string;
  state: string;
  city: string;
  study_type: string;
  paid: string;
  posted_within: string;
  search: string;
}

interface FilterBarProps {
  filters: FilterState;
  onChange: (key: keyof FilterState, value: string) => void;
  onReset: () => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({ filters, onChange, onReset }) => {
  return (
    <div className="bg-slate-900/60 backdrop-blur border border-slate-800 rounded-2xl p-4 shadow-xl space-y-3">
      {/* Search Input and Country Buttons */}
      <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search research studies, focus groups, universities, surveys..."
            value={filters.search}
            onChange={(e) => onChange('search', e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-sm bg-slate-950/70 border border-slate-800 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
          />
        </div>

        {/* Country Quick Filters */}
        <div className="flex items-center space-x-1.5 p-1 bg-slate-950/70 border border-slate-800 rounded-xl">
          <button
            onClick={() => onChange('country', '')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              filters.country === ''
                ? 'bg-cyan-500 text-white shadow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            All Regions
          </button>
          <button
            onClick={() => onChange('country', 'US')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center space-x-1 ${
              filters.country === 'US'
                ? 'bg-blue-600 text-white shadow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <span>🇺🇸</span>
            <span>United States</span>
          </button>
          <button
            onClick={() => onChange('country', 'CA')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center space-x-1 ${
              filters.country === 'CA'
                ? 'bg-red-600 text-white shadow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <span>🇨🇦</span>
            <span>Canada</span>
          </button>
        </div>
      </div>

      {/* Granular Filters Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-1 border-t border-slate-800/60">
        {/* Freshness Window */}
        <div>
          <label className="block text-[10px] uppercase font-semibold tracking-wider text-slate-400 mb-1 flex items-center space-x-1">
            <Clock className="w-3 h-3 text-emerald-400" />
            <span>Freshness</span>
          </label>
          <select
            value={filters.posted_within}
            onChange={(e) => onChange('posted_within', e.target.value)}
            className="w-full px-2.5 py-1.5 text-xs bg-slate-950/80 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="7d">Within 7 Days (Default)</option>
            <option value="3d">Within 3 Days</option>
            <option value="24h">Within 24 Hours</option>
            <option value="">All Time (Archived)</option>
          </select>
        </div>

        {/* State / Province */}
        <div>
          <label className="block text-[10px] uppercase font-semibold tracking-wider text-slate-400 mb-1 flex items-center space-x-1">
            <MapPin className="w-3 h-3 text-cyan-400" />
            <span>State / Province</span>
          </label>
          <input
            type="text"
            placeholder="e.g. Arizona, Ontario..."
            value={filters.state}
            onChange={(e) => onChange('state', e.target.value)}
            className="w-full px-2.5 py-1.5 text-xs bg-slate-950/80 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500"
          />
        </div>

        {/* City */}
        <div>
          <label className="block text-[10px] uppercase font-semibold tracking-wider text-slate-400 mb-1 flex items-center space-x-1">
            <MapPin className="w-3 h-3 text-cyan-400" />
            <span>City</span>
          </label>
          <input
            type="text"
            placeholder="e.g. Phoenix, Toronto..."
            value={filters.city}
            onChange={(e) => onChange('city', e.target.value)}
            className="w-full px-2.5 py-1.5 text-xs bg-slate-950/80 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500"
          />
        </div>

        {/* Study Type */}
        <div>
          <label className="block text-[10px] uppercase font-semibold tracking-wider text-slate-400 mb-1 flex items-center space-x-1">
            <Filter className="w-3 h-3 text-purple-400" />
            <span>Study Type</span>
          </label>
          <select
            value={filters.study_type}
            onChange={(e) => onChange('study_type', e.target.value)}
            className="w-full px-2.5 py-1.5 text-xs bg-slate-950/80 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Study Types</option>
            <option value="paid_survey">Paid Survey</option>
            <option value="focus_group">Focus Group</option>
            <option value="user_interview">User Interview</option>
            <option value="usability_test">Usability Test</option>
            <option value="academic_survey">Academic Survey</option>
            <option value="diary_study">Diary Study</option>
            <option value="research_study">Research Study</option>
          </select>
        </div>

        {/* Compensation */}
        <div>
          <label className="block text-[10px] uppercase font-semibold tracking-wider text-slate-400 mb-1 flex items-center space-x-1">
            <DollarSign className="w-3 h-3 text-amber-400" />
            <span>Compensation</span>
          </label>
          <select
            value={filters.paid}
            onChange={(e) => onChange('paid', e.target.value)}
            className="w-full px-2.5 py-1.5 text-xs bg-slate-950/80 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Rewards</option>
            <option value="true">Paid Only ($)</option>
            <option value="false">Unpaid / Volunteer</option>
          </select>
        </div>

        {/* Reset Filter Button */}
        <div className="flex items-end">
          <button
            onClick={onReset}
            className="w-full px-3 py-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 flex items-center justify-center space-x-1.5 transition"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Reset Filters</span>
          </button>
        </div>
      </div>
    </div>
  );
};
