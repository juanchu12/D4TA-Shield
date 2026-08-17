"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Upload, FileText, Loader2 } from "lucide-react";
import { GlassCard, RiskBadge } from "@/components";
import {
  analyzeContract,
  listContracts,
  uploadContract,
  type ContractSummary,
} from "@/lib/api";
import { brand } from "@/lib/brand";

export default function DashboardPage() {
  const [contracts, setContracts] = useState<ContractSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const res = await listContracts();
      setContracts(res.data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const { data } = await uploadContract(file);
      await analyzeContract(data.id);
      await refresh();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error al subir");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold text-ink">Contratos</h1>
          <p className="mt-1 text-sm text-muted">Borradores en revisión antes de firma</p>
        </div>
        <label
          className="flex cursor-pointer items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium text-white"
          style={{ background: brand.colors.indigo }}
        >
          {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
          Subir borrador
          <input type="file" accept=".pdf,.docx" className="hidden" onChange={onUpload} disabled={uploading} />
        </label>
      </div>

      {loading ? (
        <p className="text-muted">Cargando…</p>
      ) : contracts.length === 0 ? (
        <GlassCard>
          <p className="text-muted">No hay contratos. Sube un PDF o DOCX para empezar.</p>
        </GlassCard>
      ) : (
        <div className="grid gap-4">
          {contracts.map((c) => (
            <Link key={c.id} href={`/contracts/${c.id}`}>
              <GlassCard className="transition hover:border-[var(--indigo)]">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex gap-3">
                    <FileText className="mt-1 h-5 w-5 text-[var(--indigo)]" />
                    <div>
                      <h2 className="font-medium text-ink">{c.filename}</h2>
                      <p className="mt-1 font-mono text-xs text-muted">
                        {c.status} · {c.clause_count} cláusulas
                        {c.discrepancy_count > 0 && ` · ${c.discrepancy_count} discrepancias`}
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <RiskBadge level="alto" count={c.risk_counts.alto} />
                    <RiskBadge level="medio" count={c.risk_counts.medio} />
                    <RiskBadge level="bajo" count={c.risk_counts.bajo} />
                  </div>
                </div>
              </GlassCard>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
