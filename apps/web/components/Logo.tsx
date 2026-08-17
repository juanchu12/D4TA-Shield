import { brand } from "@/lib/brand";

export function Logo({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const textSize = size === "sm" ? "text-base" : size === "lg" ? "text-2xl" : "text-xl";
  return (
    <div className="flex items-center gap-2">
      <div
        className="flex h-9 w-9 items-center justify-center rounded-xl font-mono text-sm font-bold"
        style={{ background: brand.colors.indigoBg, color: brand.colors.indigo }}
      >
        S
      </div>
      <span className={`font-display font-bold tracking-tight text-ink ${textSize}`}>
        {brand.product}
      </span>
    </div>
  );
}
