import { progressData, costData, safetyData } from '../data/dummyData';

function SummaryItem({ label, value, sub, color }) {
  return (
    <div className="flex flex-col items-center px-6 py-3 border-r border-slate-700 last:border-r-0">
      <p className="text-xs text-slate-400 mb-1">{label}</p>
      <p className={`text-xl font-bold ${color}`}>{value}</p>
      {sub && <p className="text-xs text-slate-500 mt-0.5">{sub}</p>}
    </div>
  );
}

export default function SummaryBar() {
  const sites = ['A', 'B', 'C'];

  const avgActual = sites.reduce((s, id) => s + progressData[id].actual, 0) / 3;
  const avgPlanned = sites.reduce((s, id) => s + progressData[id].planned, 0) / 3;
  const overBudgetCount = sites.filter((id) => costData[id].overBudget).length;
  const totalPending = sites.reduce((s, id) => s + safetyData[id].pendingActions, 0);
  const minNoAccident = Math.min(...sites.map((id) => safetyData[id].noAccidentDays));
  const dangerSites = sites.filter((id) => progressData[id].status === 'danger').length;

  return (
    <div className="bg-slate-800/80 border border-slate-700 rounded-xl flex items-stretch overflow-hidden">
      <SummaryItem
        label="전체 평균 공정률"
        value={`${avgActual.toFixed(1)}%`}
        sub={`계획 ${avgPlanned.toFixed(1)}%`}
        color={avgActual >= avgPlanned ? 'text-emerald-400' : 'text-amber-400'}
      />
      <SummaryItem
        label="공정 위험 현장"
        value={`${dangerSites}개소`}
        sub="즉시 조치 필요"
        color={dangerSites > 0 ? 'text-red-400' : 'text-emerald-400'}
      />
      <SummaryItem
        label="예산 초과 현장"
        value={`${overBudgetCount}개소`}
        sub={`전체 ${sites.length}개소 중`}
        color={overBudgetCount > 0 ? 'text-red-400' : 'text-emerald-400'}
      />
      <SummaryItem
        label="전체 미결 안전조치"
        value={`${totalPending}건`}
        sub="3개 현장 합산"
        color={totalPending > 15 ? 'text-red-400' : totalPending > 8 ? 'text-amber-400' : 'text-emerald-400'}
      />
      <SummaryItem
        label="최단 무재해 일수"
        value={`${minNoAccident}일`}
        sub="현장 중 최소값"
        color={minNoAccident < 50 ? 'text-amber-400' : 'text-emerald-400'}
      />
    </div>
  );
}
