import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { formatBillion } from '../data/dummyData';

function RateGauge({ rate, plannedRate, overBudget }) {
  const barColor = overBudget ? '#f87171' : '#60a5fa';
  const planColor = '#94a3b8';

  return (
    <div className="relative h-6 bg-slate-700 rounded-full overflow-hidden">
      <div
        className="h-full rounded-full transition-all"
        style={{ width: `${Math.min(rate, 100)}%`, backgroundColor: barColor }}
      />
      <div
        className="absolute top-0 h-full w-0.5 bg-white/70"
        style={{ left: `${plannedRate}%` }}
        title={`계획: ${plannedRate}%`}
      />
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

export default function CostCard({ site, data }) {
  const diff = data.rate - data.plannedRate;
  const isOver = diff > 0;

  return (
    <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-base font-bold text-white">{site.name}</h3>
          <p className="text-xs text-slate-400 mt-0.5">{site.location} · {site.type}</p>
        </div>
        {data.overBudget ? (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border bg-red-500/20 text-red-400 border-red-500/40">
            <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
            예산 초과
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border bg-emerald-500/20 text-emerald-400 border-emerald-500/40">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            예산 내
          </span>
        )}
      </div>

      <div>
        <div className="flex justify-between text-xs text-slate-400 mb-2">
          <span>실행원가 집행률</span>
          <span className={`font-bold text-sm ${data.overBudget ? 'text-red-400' : 'text-emerald-400'}`}>
            {data.rate.toFixed(1)}%
          </span>
        </div>
        <RateGauge rate={data.rate} plannedRate={data.plannedRate} overBudget={data.overBudget} />
        <div className="flex justify-between text-xs mt-1.5">
          <span className="text-slate-500">계획 집행률: {data.plannedRate.toFixed(1)}%</span>
          <span className={`font-semibold ${isOver ? 'text-red-400' : 'text-emerald-400'}`}>
            {isOver ? '+' : ''}{diff.toFixed(1)}%p
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="bg-slate-900/50 rounded-lg p-3">
          <p className="text-slate-400 mb-0.5">예산</p>
          <p className="text-slate-200 font-semibold">{formatBillion(data.budget)}</p>
        </div>
        <div className="bg-slate-900/50 rounded-lg p-3">
          <p className="text-slate-400 mb-0.5">집행액</p>
          <p className="text-slate-200 font-semibold">{formatBillion(data.executed)}</p>
        </div>
      </div>

      {data.overBudget && (
        <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-xs">
          <span className="text-red-400 text-base">⚠</span>
          <div>
            <p className="text-red-400 font-semibold">예산 초과 {formatBillion(data.overAmount)}</p>
            <p className="text-slate-400 mt-0.5">준공 시 예상: {formatBillion(data.forecast)}</p>
          </div>
        </div>
      )}

      <div>
        <p className="text-xs text-slate-400 mb-2">월별 집행률 추이</p>
        <ResponsiveContainer width="100%" height={110}>
          <AreaChart data={data.monthly} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
            <defs>
              <linearGradient id={`grad-${site.id}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={data.overBudget ? '#f87171' : '#60a5fa'} stopOpacity={0.3} />
                <stop offset="95%" stopColor={data.overBudget ? '#f87171' : '#60a5fa'} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="month" tick={{ fill: '#94a3b8', fontSize: 10 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} domain={['auto', 'auto']} />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="planned"
              name="계획"
              stroke="#94a3b8"
              strokeWidth={1.5}
              strokeDasharray="4 2"
              fill="none"
            />
            <Area
              type="monotone"
              dataKey="actual"
              name="실적"
              stroke={data.overBudget ? '#f87171' : '#60a5fa'}
              strokeWidth={2}
              fill={`url(#grad-${site.id})`}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
