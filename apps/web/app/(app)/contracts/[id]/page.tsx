"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { AlertOctagon, CheckCircle2, Loader2 } from "lucide-react";
import { GlassCard, RiskBadge } from "@/components";
import { getReport, reviewFlag } from "@/lib/api";
import { brand, riskColor, type RiskLevel } from "@/lib/brand";

type Clause = {
  id: string;
  index: number;
  title: string;
  text: string;
};

type Analysis = {
  clause_id: string;
  category: string;
  risk_level: RiskLevel;
  explanation: string;
  quoted_evidence: string;
  detected_by: string;
  requires_priority_review: boolean;
  discrepancy_reason?: string;
};

type Flag = {
  id: string;
  engine_clause_id: string;
  risk_level: RiskLevel;
  human_reviewed: boolean;
};

export default function ContractPage() {
  const { id } = useParams<{ id: string }>();
  const [clauses, setClauses] = useState<Clause[]>([]);
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [flags, setFlags] = useState<Flag[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [filename, setFilename] = useState("");
  const [loading, setLoading] = useState(true);
  const [reviewing, setReviewing] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getReport(id);
      const data = res.data;
      setFilename(String(data.filename ?? ""));
      setClauses((data.clauses as Clause[]) ?? []);
      setAnalyses((data.analyses as Analysis[]) ?? []);
      setFlags((data.flags as Flag[]) ?? []);
      if (!selected && (data.analyses as Analysis[])?.[0]) {
        setSelected((data.analyses as Analysis[])[0].clause_id);
      }
    } finally {
      setLoading(false);
    }
  }, [id, selected]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const analysisMap = Object.fromEntries(analyses.map((a) => [a.clause_id, a]));
  const flagMap = Object.fromEntries(flags.map((f) => [f.engine_clause_id, f]));
  const selectedAnalysis = selected ? analysisMap[selected] : null;
  const selectedFlag = selected ? flagMap[selected] : null;

  async function markReviewed() {
    if (!selectedFlag) return;
    setReviewing(selectedFlag.id);
    try {
      await reviewFlag(id, selectedFlag.id);
      await refresh();
    } finally {
      setReviewing(null);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-muted">
        <Loader2 className="h-4 w-4 animate-spin" /> Cargando contrato…
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">{filename}</h1>
          <Link href="/discrepancies" className="mt-1 inline-flex items-center gap-1 text-sm text-[var(--indigo)]">
            <AlertOctagon className="h-4 w-4" />
            Ver discrepancias prioritarias
          </Link>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_380px]">
        <GlassCard className="max-h-[70vh] overflow-auto">
          <h2 className="font-display mb-4 text-lg font-semibold">Documento</h2>
          <div className="space-y-4">
            {clauses.map((clause) => {
              const a = analysisMap[clause.id];
              const level = a?.risk_level ?? "bajo";
              const highlight =
                level === "alto"
                  ? "clause-highlight-alto"
                  : level === "medio"
                    ? "clause-highlight-medio"
                    : a
                      ? "clause-highlight-bajo"
                      : "";
              return (
                <button
                  key={clause.id}
                  type="button"
                  onClick={() => setSelected(clause.id)}
                  className={`block w-full rounded-xl p-4 text-left transition ${highlight} ${
                    selected === clause.id ? "ring-1 ring-[var(--indigo)]" : ""
                  }`}
                >
                  <p className="font-mono text-xs text-muted">{clause.title}</p>
                  <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-ink">{clause.text}</p>
                </button>
              );
            })}
          </div>
        </GlassCard>

        <GlassCard className="sticky top-4 h-fit">
          <h2 className="font-display mb-3 text-lg font-semibold">Cláusula señalada</h2>
          {!selectedAnalysis ? (
            <p className="text-sm text-muted">Selecciona una cláusula resaltada.</p>
          ) : (
            <div className="space-y-3">
              <RiskBadge level={selectedAnalysis.risk_level} />
              <p className="font-mono text-xs uppercase text-muted">{selectedAnalysis.category}</p>
              <p className="text-sm text-ink">{selectedAnalysis.explanation}</p>
              <blockquote
                className="rounded-lg border-l-2 pl-3 font-mono text-xs leading-relaxed text-muted"
                style={{ borderColor: riskColor(selectedAnalysis.risk_level) }}
              >
                {selectedAnalysis.quoted_evidence}
              </blockquote>
              <p className="font-mono text-[10px] text-muted-soft">
                Detectado por: {selectedAnalysis.detected_by}
              </p>
              {selectedAnalysis.requires_priority_review && (
                <p className="text-xs text-[var(--risk-medium)]">
                  ⚠ Revisión prioritaria: {selectedAnalysis.discrepancy_reason}
                </p>
              )}
              {selectedFlag && selectedAnalysis.risk_level === "alto" && (
                <button
                  type="button"
                  onClick={markReviewed}
                  disabled={selectedFlag.human_reviewed || reviewing !== null}
                  className="flex w-full items-center justify-center gap-2 rounded-xl py-2.5 text-sm font-medium disabled:opacity-50"
                  style={{
                    background: selectedFlag.human_reviewed ? "rgba(52,211,153,0.15)" : brand.colors.indigoBg,
                    color: selectedFlag.human_reviewed ? "#34d399" : brand.colors.indigo,
                  }}
                >
                  {reviewing ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <CheckCircle2 className="h-4 w-4" />
                  )}
                  {selectedFlag.human_reviewed ? "Revisada (auditada)" : "Marcar como revisada"}
                </button>
              )}
            </div>
          )}
        </GlassCard>
      </div>
    </div>
  );
}
