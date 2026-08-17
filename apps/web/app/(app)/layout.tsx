"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LayoutDashboard, FileText, AlertOctagon, LogOut } from "lucide-react";
import { Logo, CategoryTag, LegalDisclaimer } from "@/components";
import { clearToken } from "@/lib/api";
import { brand } from "@/lib/brand";

const nav = [
  { href: "/dashboard", label: "Contratos", icon: LayoutDashboard },
  { href: "/discrepancies", label: "Discrepancias", icon: AlertOctagon },
];

export default function AppShellLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  function logout() {
    clearToken();
    router.push("/login");
    router.refresh();
  }

  return (
    <div className="relative flex min-h-screen">
      <aside className="sticky top-0 flex h-screen w-[240px] shrink-0 flex-col border-r border-[var(--glass-brd)] bg-[rgba(7,10,20,0.72)] px-4 py-5 backdrop-blur-xl">
        <div className="mb-2 px-1">
          <Logo size="sm" />
        </div>
        <div className="mb-6 mt-3 px-1">
          <CategoryTag />
        </div>
        <nav className="flex flex-1 flex-col gap-1">
          {nav.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition"
                style={{
                  color: active ? brand.colors.indigo : brand.colors.muted,
                  background: active ? brand.colors.indigoBg : "transparent",
                }}
              >
                <Icon className="h-4 w-4" />
                <span className={active ? "font-medium text-ink" : ""}>{label}</span>
              </Link>
            );
          })}
        </nav>
        <button
          type="button"
          onClick={logout}
          className="mt-4 flex items-center gap-2 rounded-xl px-3 py-2.5 text-sm text-muted hover:text-[var(--risk-high)]"
        >
          <LogOut className="h-4 w-4" />
          Cerrar sesión
        </button>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-[var(--glass-brd)] bg-[rgba(7,10,20,0.45)] px-6 py-3 backdrop-blur-md">
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
            {brand.company} · {brand.tagline}
          </p>
          <div className="mt-3">
            <LegalDisclaimer compact />
          </div>
        </header>
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
