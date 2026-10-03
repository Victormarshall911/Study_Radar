'use client';

import React from 'react';
import { Radar, Activity, Globe, Database, Compass, BellRing } from 'lucide-react';

interface NavbarProps {
  activeTab: 'radar' | 'sources' | 'ingest' | 'analytics';
  setActiveTab: (tab: 'radar' | 'sources' | 'ingest' | 'analytics') => void;
  onTestNotification: () => void;
  isTestingNotification: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onTestNotification,
  isTestingNotification,
}) => {
  return (
    <header className="sticky top-0 z-40 backdrop-blur-md bg-slate-950/80 border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('radar')}>
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20 text-white">
            <Radar className="w-6 h-6 animate-pulse" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-cyan-400 bg-clip-text text-transparent">
                Study Radar
              </span>
              <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wider uppercase rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800">
                US & CA 7-Day
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Continuous Research & Survey Discovery</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2">
          <button
            onClick={() => setActiveTab('radar')}
            className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all ${
              activeTab === 'radar'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Compass className="w-4 h-4" />
            <span>Live Radar</span>
          </button>

          <button
            onClick={() => setActiveTab('sources')}
            className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all ${
              activeTab === 'sources'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Database className="w-4 h-4" />
            <span>Sources</span>
          </button>

          <button
            onClick={() => setActiveTab('ingest')}
            className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all ${
              activeTab === 'ingest'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>Inspector</span>
          </button>
        </nav>

        {/* Actions */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onTestNotification}
            disabled={isTestingNotification}
            title="Dispatch local test alert"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            <BellRing className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden sm:inline">{isTestingNotification ? 'Sending...' : 'Test Alert'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
