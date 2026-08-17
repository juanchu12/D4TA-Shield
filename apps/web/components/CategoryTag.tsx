import { brand } from "@/lib/brand";

export function CategoryTag() {
  return (
    <span
      className="inline-block rounded-full px-3 py-1 font-mono text-[10px] uppercase tracking-wider"
      style={{ background: brand.colors.indigoBg, color: brand.colors.indigo }}
    >
      {brand.category}
    </span>
  );
}
