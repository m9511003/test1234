import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from 'recharts';
import StatusBadge from './StatusBadge';

function CircleGauge({ value, color }) {
  return (
    <div className="relative w-24 h-24 mx-auto">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          cx="50%"
          cy="50%"
          innerRadius="70%"
          outerRadius="100%"
          data={[{ value, fill: color }]}
          startAngle={90}
          endAngle={-270}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
          <RadialBar
            background={{ fill: '#1e293b' }}
            dataKey="value"
            cornerRadius={6}
            angleAxisId={0}
          />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-lg font-bold text-white">{value}%</span>
        <span className="text-xs text-slate-400">점검완료</span>
      </div>
    </div>
  );
}

const gaugeColor = { low: '#34d399', medium: '#fbbf24', high: '#f87171' };

export default function SafetyCard({ site, data }) {
  const color = gaugeColor[data.riskLevel];

  return (
    <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-base font-bold text-white">{site.name}</h3>
          <p className="text-xs text-slate-400 mt-0.5">{site.location} · {site.type}</p>
        </div>
        <StatusBadge status={data.riskLevel} />
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="bg-slate-900/50 rounded-lg p-3">
          <p className="text-2xl font-bold text-white">{data.noAccidentDays}</p>
          <p className="text-xs text-slate-400 mt-0.5">무재해 일수</p>
        </div>
        <div className="bg-slate-900/50 rounded-lg p-3">
          <p className={`text-2xl font-bold ${data.pendingActions > 10 ? 'text-red-400' : data.pendingActions > 5 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {data.pendingActions}
          </p>
          <p className="text-xs text-slate-400 mt-0.5">미결 조치</p>
        </div>
        <div className="bg-slate-900/50 rounded-lg p-3">
          <p className={`text-2xl font-bold ${data.nearMiss >= 3 ? 'text-red-400' : data.nearMiss >= 1 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {data.nearMiss}
          </p>
          <p className="text-xs text-slate-400 mt-0.5">아차사고</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <CircleGauge value={data.inspectionRate} color={color} />
        <div className="flex-1 space-y-1.5">
          {data.inspections.map((item) => (
            <div key={item.category} className="flex items-center justify-between text-xs">
              <span className="text-slate-400">{item.category}</span>
              {item.completed ? (
                <span className="text-emerald-400 font-semibold flex items-center gap-1">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                  완료
                </span>
              ) : (
                <span className="text-red-400 font-semibold flex items-center gap-1">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  미완료
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {data.pendingActions > 5 && (
        <div className={`flex items-center gap-2 rounded-lg p-3 text-xs border ${
          data.pendingActions > 10
            ? 'bg-red-500/10 border-red-500/30'
            : 'bg-amber-500/10 border-amber-500/30'
        }`}>
          <span className={`text-base ${data.pendingActions > 10 ? 'text-red-400' : 'text-amber-400'}`}>⚠</span>
          <p className={`font-semibold ${data.pendingActions > 10 ? 'text-red-400' : 'text-amber-400'}`}>
            미결 조치 {data.pendingActions}건 — 즉시 대응 필요
          </p>
        </div>
      )}
    </div>
  );
}
