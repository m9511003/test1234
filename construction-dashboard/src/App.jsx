import { useState } from 'react';
import { sites, progressData, costData, safetyData, reportMeta } from './data/dummyData';
import ProgressCard from './components/ProgressCard';
import CostCard from './components/CostCard';
import SafetyCard from './components/SafetyCard';
import SummaryBar from './components/SummaryBar';

const TABS = [
  { id: 'progress', label: '공정률', icon: '📊' },
  { id: 'cost',     label: '원가',   icon: '💰' },
  { id: 'safety',   label: '안전',   icon: '🦺' },
];

function TabButton({ tab, active, onClick }) {
  return (
    <button
      onClick={() => onClick(tab.id)}
      className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
        active
          ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/40'
          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
      }`}
    >
      <span>{tab.icon}</span>
      {tab.label}
    </button>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState('progress');

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-700/80 sticky top-0 z-10 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                  건
                </div>
                <div>
                  <h1 className="text-lg font-bold text-white leading-tight">
                    {reportMeta.year}년 제{reportMeta.week}주차 주간 현장보고
                  </h1>
                  <p className="text-xs text-slate-400">기준일: {reportMeta.reportDate} · 담당: 현장관리팀</p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-500 bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5">
                대상 현장 3개소
              </span>
              <span className="text-xs text-slate-500 bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5">
                임원 보고용
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* Summary */}
        <section>
          <div className="flex items-center gap-2 mb-3">
            <span className="w-1 h-4 bg-blue-500 rounded-full inline-block" />
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">종합 현황</h2>
          </div>
          <SummaryBar />
        </section>

        {/* Tab Navigation */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-1 bg-slate-800/60 border border-slate-700 rounded-xl p-1">
              {TABS.map((tab) => (
                <TabButton
                  key={tab.id}
                  tab={tab}
                  active={activeTab === tab.id}
                  onClick={setActiveTab}
                />
              ))}
            </div>
            <div className="hidden md:flex items-center gap-3 text-xs text-slate-500">
              <span className="flex items-center gap-1.5">
                <span className="inline-block w-6 border-t-2 border-dashed border-blue-400" />
                계획
              </span>
              <span className="flex items-center gap-1.5">
                <span className="inline-block w-6 border-t-2 border-emerald-400" />
                실적
              </span>
            </div>
          </div>

          {/* Tab Content */}
          {activeTab === 'progress' && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="w-1 h-4 bg-blue-500 rounded-full inline-block" />
                <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">현장별 공정률 현황</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {sites.map((site) => (
                  <ProgressCard key={site.id} site={site} data={progressData[site.id]} />
                ))}
              </div>
            </div>
          )}

          {activeTab === 'cost' && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="w-1 h-4 bg-blue-500 rounded-full inline-block" />
                <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">현장별 원가 집행 현황</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {sites.map((site) => (
                  <CostCard key={site.id} site={site} data={costData[site.id]} />
                ))}
              </div>
            </div>
          )}

          {activeTab === 'safety' && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="w-1 h-4 bg-blue-500 rounded-full inline-block" />
                <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">현장별 안전 관리 현황</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {sites.map((site) => (
                  <SafetyCard key={site.id} site={site} data={safetyData[site.id]} />
                ))}
              </div>
            </div>
          )}
        </section>

        {/* Footer note */}
        <footer className="border-t border-slate-800 pt-4 pb-8">
          <p className="text-xs text-slate-600 text-center">
            본 보고서는 현장관리팀에서 주간 취합한 데이터를 기반으로 작성되었습니다.
            문의: 현장관리팀 (내선 1234) · 자동 생성 기준일 {reportMeta.reportDate}
          </p>
        </footer>
      </main>
    </div>
  );
}
