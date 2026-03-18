const SERIES_COLOR_COUNT = 60

/** Разнесённые по кругу оттенки (золотой угол) для до 60 рядов */
function buildSeriesColors(count: number): string[] {
  const colors: string[] = []
  const golden = 137.508
  for (let i = 0; i < count; i++) {
    const h = (i * golden) % 360
    const s = 58 + (i % 6) * 5
    const l = 42 + (i % 5) * 5
    colors.push(`hsl(${h.toFixed(1)} ${s}% ${l}%)`)
  }
  return colors
}

export const SERIES_COLORS: string[] = buildSeriesColors(SERIES_COLOR_COUNT)

export function getSeriesColor(index: number, override?: string): string {
  if (override) return override
  return SERIES_COLORS[index % SERIES_COLORS.length]
}
