import { riskColor, type RiskLevel } from "@/lib/brand";

export function RiskBadge({ level, count }: { level: RiskLevel; count?: number }) {
  const color = riskColor(level);
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 font-mono text-[10px] uppercase tracking-wide"
      style={{ background: `${color}22`, color }}
    >
      {level}
      {count !== undefined && <span className="font-display text-sm font-bold">{count}</span>}
    </span>
  );
}
