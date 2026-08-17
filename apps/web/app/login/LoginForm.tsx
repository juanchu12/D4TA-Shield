"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Logo, CategoryTag, LegalDisclaimer } from "@/components";
import { login, setToken } from "@/lib/api";
import { brand } from "@/lib/brand";

export default function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const [email, setEmail] = useState("legal@demo.d4ta.local");
  const [password, setPassword] = useState("legal123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const { token } = await login(email, password);
      setToken(token);
      router.push(params.get("next") || "/dashboard");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error de autenticación");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="glass-panel w-full max-w-md p-8">
        <Logo />
        <div className="mt-3">
          <CategoryTag />
        </div>
        <h1 className="font-display mt-6 text-2xl font-bold text-ink">Acceso por tenant</h1>
        <p className="mt-2 text-sm text-muted">Segunda lectura contractual — no asesoría legal.</p>
        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <label className="block text-sm">
            <span className="text-muted">Email</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-xl border border-[var(--glass-brd)] bg-[var(--void2)] px-3 py-2 text-ink outline-none focus:border-[var(--indigo)]"
              required
            />
          </label>
          <label className="block text-sm">
            <span className="text-muted">Contraseña</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-xl border border-[var(--glass-brd)] bg-[var(--void2)] px-3 py-2 text-ink outline-none focus:border-[var(--indigo)]"
              required
            />
          </label>
          {error && <p className="text-sm text-[var(--risk-high)]">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl py-2.5 font-medium text-white transition hover:opacity-90 disabled:opacity-50"
            style={{ background: brand.colors.indigo }}
          >
            {loading ? "Entrando…" : "Entrar"}
          </button>
        </form>
        <div className="mt-6">
          <LegalDisclaimer compact />
        </div>
      </div>
    </div>
  );
}
