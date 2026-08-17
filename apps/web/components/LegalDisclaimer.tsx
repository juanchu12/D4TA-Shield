"use client";

import { AlertTriangle } from "lucide-react";
import { brand } from "@/lib/brand";

export function LegalDisclaimer({ compact = false }: { compact?: boolean }) {
  return (
    <div
      className={`flex gap-3 rounded-[var(--radius-panel)] border px-4 py-3 ${compact ? "text-xs" : "text-sm"}`}
      style={{
        background: "rgba(245, 165, 36, 0.08)",
        borderColor: "rgba(245, 165, 36, 0.25)",
        color: brand.colors.ink,
      }}
      role="note"
      aria-label="Aviso legal"
    >
      <AlertTriangle
        className="mt-0.5 h-4 w-4 shrink-0"
        style={{ color: brand.colors.riskMedium }}
        aria-hidden
      />
      <p className="leading-relaxed">{brand.disclaimer}</p>
    </div>
  );
}
