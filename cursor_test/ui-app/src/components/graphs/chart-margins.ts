export const CHART_MARGINS = {
  top: 16,
  right: 20,
  bottom: 44,
  left: 56,
} as const

export function getPlotSize(width: number, height: number): { plotW: number; plotH: number } {
  return {
    plotW: Math.max(1, width - CHART_MARGINS.left - CHART_MARGINS.right),
    plotH: Math.max(1, height - CHART_MARGINS.top - CHART_MARGINS.bottom),
  }
}
