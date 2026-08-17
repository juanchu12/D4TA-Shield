import Link from "next/link";
import { Logo, CategoryTag, LegalDisclaimer } from "@/components";
import { brand } from "@/lib/brand";

export default function HomePage() {
  return (
    <div className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6 py-16">
      <Logo size="lg" />
      <div className="mt-4">
        <CategoryTag />
      </div>
      <h1 className="font-display mt-8 text-4xl font-bold leading-tight text-ink">
        Segunda lectura contractual antes de la firma
      </h1>
      <p className="mt-4 text-lg text-muted">{brand.tagline}</p>
      <div className="mt-8 flex gap-4">
        <Link
          href="/login"
          className="rounded-xl px-6 py-3 font-medium text-white"
          style={{ background: brand.colors.indigo }}
        >
          Acceder
        </Link>
        <Link
          href="/dashboard"
          className="glass-panel rounded-xl px-6 py-3 font-medium text-ink"
        >
          Demo
        </Link>
      </div>
      <div className="mt-10">
        <LegalDisclaimer />
      </div>
    </div>
  );
}
