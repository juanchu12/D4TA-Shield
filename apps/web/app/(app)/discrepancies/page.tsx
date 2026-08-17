"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AlertOctagon, Loader2 } from "lucide-react";
import { GlassCard, RiskBadge } from "@/components";
import { listContracts, getDiscrepancies } from "@/lib/api";
import { brand, type RiskLevel } from "@/lib/brand";

type Discrepancy = {
  clause_id: string;
  category: string;
  risk_level: RiskLevel;
  explanation: string;
  quoted_evidence: string;
  discrepancy_reason?: string;
};

export default function DiscrepanciesPage() {
  const [items, setItems] = useState<{ contractId: string; filename: string; discrepancies: Discrepancy[] }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const { data: contracts } = await listContracts();
        const withDisc = contracts.filter((c) => c.discrepancy_count > 0);
        const results = await Promise.all(
          withDisc.map(async (c) => {
            const res = await getDiscrepancies(c.id);
            return {
              contractId: c.id,
              filename: c.filename,
              discrepancies: res.data as Discrepancy[],
            };
          }),
        );
        setItems(results.filter((r) => r.discrepancies.length > 0));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display flex items-center gap-2 text-3xl font-bold text-ink">
          <AlertOctagon style={{ color: brand.colors.riskMedium }} />
          Discrepancias
        </h1>
        <p className="mt-1 text-sm text-muted">
          Cláusulas donde la capa de reglas y el LLM no coincidieron — revisión prioritaria.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-muted">
          <Loader2 className="h-4 w-4 animate-spin" /> Cargando…
        </div>
      ) : items.length === 0 ? (
        <GlassCard>
          <p className="text-muted">No hay discrepancias pendientes.</p>
        </GlassCard>
      ) : (
        items.map(({ contractId, filename, discrepancies }) => (
          <GlassCard key={contractId}>
            <Link href={`/contracts/${contractId}`} className="font-display text-lg font-semibold text-[var(--indigo)]">
              {filename}
            </Link>
            <div className="mt-4 space-y-3">
              {discrepancies.map((d) => (
                <div
                  key={d.clause_id}
                  className="rounded-xl border border-[var(--glass-brd)] p-4"
                  style={{ background: "rgba(245,165,36,0.06)" }}
                >
                  <div className="flex items-center gap-2">
                    <RiskBadge level={d.risk_level} />
                    <span className="font-mono text-xs text-muted">{d.category}</span>
                  </div>
                  <p className="mt-2 text-sm">{d.explanation}</p>
                  <blockquote className="mt-2 font-mono text-xs text-muted">{d.quoted_evidence}</blockquote>
                  {d.discrepancy_reason && (
                    <p className="mt-2 text-xs text-[var(--risk-medium)]">{d.discrepancy_reason}</p>
                  )}
                </div>
              ))}
            </div>
          </GlassCard>
        ))
      )}
    </div>
  );
}
