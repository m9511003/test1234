import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import StatusBadge from './StatusBadge';

function GaugeBar({ planned, actual }) {
  const diff = actual - planned;
  const isAhead = diff >= 0;
  return (
    <div className="space-y-2">
      <div>
        <div className="flex justify-between text-xs text-slate-400 mb-1">
          <span>계획 공정률</span>
          <span className="text-slate-200 font-medium">{planned.toFixed(1)}%</span>
        </div>
        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 rounded-full transition-all"
            style={{ width: `${planned}%` }}
          />
        </div>
      </div>
      <div>
        <div className="flex justify-between text-xs text-slate-400 mb-1">
          <span>실적 공정률</span>
          <span className={`font-semibold ${isAhead ? 'text-emerald-400' : 'text-red-400'}`}>
            {actual.toFixed(1)}%
          </span>
        </div>
        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${isAhead ? 'bg-emerald-500' : 'bg-red-500'}`}
            style={{ width: `${actual}%` }}
          />
        </div>
      </div>
      <div className="flex items-center gap-1.5 text-xs mt-1">
        <span className="text-slate-400">계획 대비</span>
        <span className={`font-bold ${isAhead ? 'text-emerald-400' : 'text-red-400'}`}>
          {isAhead ? '+' : ''}{diff.toFixed(1)}%p
        </span>
      </div>
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 text-xs shadow-xl">
        <p className="text-slate-300 font-medium mb-1">{label}</p>
        {payload.map((entry) => (
          <p key={entry.name} style={{ color: entry.color }} className="font-semibold">
            {entry.name}: {entry.value.toFixed(1)}%
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function ProgressCard({ site, data }) {
  return (
    <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-base font-bold text-white">{site.name}</h3>
          <p className="text-xs text-slate-400 mt-0.5">{site.location} · {site.type}</p>
        </div>
        <StatusBadge status={data.status} />
      </div>

      <GaugeBar planned={data.planned} actual={data.actual} />

      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="bg-slate-900/50 rounded-lg p-3">
          <p className="text-slate-400 mb-0.5">주간 계획</p>
          <p className="text-slate-200 font-semibold">+{data.weeklyPlanned.toFixed(1)}%p</p>
        </div>
        <div className="bg-slate-900/50 rounded-lg p-3">
          <p className="text-slate-400 mb-0.5">주간 실적</p>
          <p className={`font-semibold ${data.weeklyActual >= data.weeklyPlanned ? 'text-emerald-400' : 'text-amber-400'}`}>
            +{data.weeklyActual.toFixed(1)}%p
          </p>
        </div>
      </div>

      <div className="bg-slate-900/50 rounded-lg p-3 text-xs">
        <p className="text-slate-400 mb-0.5">현재 단계</p>
        <p className="text-slate-200 font-medium">{data.milestone}</p>
        <p className="text-slate-500 mt-1">다음 마일스톤: {data.nextMilestone}</p>
      </div>

      <div>
        <p className="text-xs text-slate-400 mb-2">5주 추이</p>
        <ResponsiveContainer width="100%" height={120}>
          <LineChart data={data.trend} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="week" tick={{ fill: '#94a3b8', fontSize: 10 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} domain={['auto', 'auto']} />
            <Tooltip content={<CustomTooltip />} />
            <Line type="monotone" dataKey="planned" name="계획" stroke="#60a5fa" strokeWidth={1.5} dot={false} strokeDasharray="4 2" />
            <Line type="monotone" dataKey="actual" name="실적" stroke="#34d399" strokeWidth={2} dot={{ r: 3, fill: '#34d399' }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
