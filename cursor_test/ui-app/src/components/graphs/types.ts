export interface TimeSeries {
  id: string
  name: string
  values: (number | null)[]
  color?: string
}

export interface TimeSeriesChartProps {
  data: TimeSeries[]
  width?: number | string
  height?: number
  showLegend?: boolean
  enableZoom?: boolean
  /** Полупрозрачная заливка под линией (тень) тем же цветом */
  showAreaFill?: boolean
  className?: string
}

export interface ChartMargins {
  top: number
  right: number
  bottom: number
  left: number
}

export interface ViewWindow {
  x0: number
  x1: number
}

export interface TooltipState {
  x: number
  y: number
  index: number
  seriesId: string
  value: number
  seriesName: string
}
