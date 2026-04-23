const configs = {
  good:    { label: '정상', bg: 'bg-emerald-500/20', text: 'text-emerald-400', border: 'border-emerald-500/40', dot: 'bg-emerald-400' },
  warning: { label: '주의', bg: 'bg-amber-500/20',   text: 'text-amber-400',   border: 'border-amber-500/40',   dot: 'bg-amber-400' },
  danger:  { label: '위험', bg: 'bg-red-500/20',     text: 'text-red-400',     border: 'border-red-500/40',     dot: 'bg-red-400' },
  low:     { label: '양호', bg: 'bg-emerald-500/20', text: 'text-emerald-400', border: 'border-emerald-500/40', dot: 'bg-emerald-400' },
  medium:  { label: '보통', bg: 'bg-amber-500/20',   text: 'text-amber-400',   border: 'border-amber-500/40',   dot: 'bg-amber-400' },
  high:    { label: '위험', bg: 'bg-red-500/20',     text: 'text-red-400',     border: 'border-red-500/40',     dot: 'bg-red-400' },
};

export default function StatusBadge({ status, label }) {
  const cfg = configs[status] || configs.good;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${cfg.bg} ${cfg.text} ${cfg.border}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      {label || cfg.label}
    </span>
  );
}
