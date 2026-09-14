"use client";

import Image from "next/image";
import { brand } from "@/lib/brand";

type LogoProps = {
  size?: "sm" | "md" | "lg";
  showWordmark?: boolean;
  className?: string;
};

const sizes = {
  sm: { badge: 28, text: "text-base" },
  md: { badge: 36, text: "text-lg" },
  lg: { badge: 48, text: "text-2xl" },
};

export function Logo({ size = "md", showWordmark = true, className = "" }: LogoProps) {
  const s = sizes[size];
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div
        className="relative shrink-0 overflow-hidden rounded-lg"
        style={{
          width: s.badge,
          height: s.badge,
          boxShadow: `0 0 18px ${brand.colors.indigo}55`,
        }}
      >
        <Image
          src="/brand/badge.png"
          alt="D4TA"
          width={s.badge}
          height={s.badge}
          className="object-contain"
          priority
        />
      </div>
      {showWordmark && (
        <div className="leading-tight">
          <div
            className={`font-display font-semibold tracking-tight text-ink ${s.text}`}
            style={{ letterSpacing: "-0.02em" }}
          >
            {brand.product}
          </div>
          <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-muted">
            {brand.category}
          </div>
        </div>
      )}
    </div>
  );
}
