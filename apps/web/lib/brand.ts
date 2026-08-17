export const brand = {
  product: "D4TA Shield",
  category: "LEGALTECH",
  company: "D4TA",
  tagline: "Segunda lectura contractual antes de la firma",
  colors: {
    void: "#070A14",
    void2: "#0B0F1F",
    indigo: "#6D5BFF",
    indigoBg: "rgba(109,91,255,0.14)",
    ink: "#EEF0FA",
    muted: "#8991AC",
    mutedSoft: "#6B7290",
    glass: "rgba(255,255,255,0.045)",
    glassBorder: "rgba(255,255,255,0.09)",
    riskMedium: "#F5A524",
    riskHigh: "#F26D6D",
    riskLow: "#8991AC",
  },
  disclaimer:
    "D4TA Shield es una segunda lectura antes de la firma, no sustituto de asesoría legal. " +
    "Este informe señala patrones de riesgo en cláusulas individuales; la decisión final es siempre humana.",
};

export type RiskLevel = "bajo" | "medio" | "alto";

export function riskColor(level: RiskLevel): string {
  switch (level) {
    case "alto":
      return brand.colors.riskHigh;
    case "medio":
      return brand.colors.riskMedium;
    default:
      return brand.colors.riskLow;
  }
}
