import { useCallback, useId, useMemo, useRef } from 'react'
import type { TimeSeries, TooltipState, ViewWindow } from './types'
import { CHART_MARGINS, getPlotSize } from './chart-margins'
import { getSeriesColor } from './utils/colors'
import { clamp, linearScale } from './utils/scales'

interface Point {
  i: number
  v: number
}

function splitSegments(values: (number | null)[]): Point[][] {
  const segments: Point[][] = []
  let current: Point[] = []
  for (let i = 0; i < values.length; i++) {
    const v = values[i]
    if (v == null) {
      if (current.length >= 2) segments.push(current)
      current = []
    } else {
      current.push({ i, v })
    }
  }
  if (current.length >= 2) segments.push(current)
  return segments
}

function formatTick(n: number): string {
  if (Math.abs(n) >= 1000) return n.toExponential(1)
  if (Number.isInteger(n)) return String(n)
  return n.toFixed(2)
}

interface ChartCanvasProps {
  width: number
  height: number
  series: TimeSeries[]
  hiddenIds: ReadonlySet<string>
  view: ViewWindow
  yMin: number
  yMax: number
  onHover: (state: TooltipState | null) => void
  isPanning: boolean
  enableZoom: boolean
  maxIndex: number
  showAreaFill: boolean
}

export function ChartCanvas({
  width,
  height,
  series,
  hiddenIds,
  view,
  yMin,
  yMax,
  onHover,
  isPanning,
  enableZoom,
  maxIndex,
  showAreaFill,
}: ChartCanvasProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const clipId = useId().replace(/:/g, '')
  const { plotW, plotH } = getPlotSize(width, height)
  const { left, top } = CHART_MARGINS
  const plotBottom = top + plotH
  const isDense = series.length > 36
  const lineStroke = isDense ? 1 : 2
  const areaOpacity = isDense ? 0.06 : 0.18

  const xScale = useMemo(
    () => linearScale([view.x0, view.x1], [left, left + plotW]),
    [view.x0, view.x1, left, plotW],
  )

  const yScale = useMemo(
    () => linearScale([yMin, yMax], [top + plotH, top]),
    [yMin, yMax, top, plotH],
  )

  const xTicks = useMemo(() => {
    const count = Math.min(8, Math.max(3, Math.floor(plotW / 80)))
    const span = view.x1 - view.x0
    const step = span / (count - 1)
    return Array.from({ length: count }, (_, k) => view.x0 + k * step)
  }, [view.x0, view.x1, plotW])

  const yTicks = useMemo(() => {
    const count = 6
    const span = yMax - yMin
    const step = span / (count - 1)
    return Array.from({ length: count }, (_, k) => yMin + k * step)
  }, [yMin, yMax])

  const handlePointerMove = useCallback(
    (clientX: number, clientY: number) => {
      if (isPanning) return
      const svg = svgRef.current
      if (!svg) return
      const rect = svg.getBoundingClientRect()
      const px = clientX - rect.left
      const py = clientY - rect.top
      if (px < left || px > left + plotW || py < top || py > top + plotH) {
        onHover(null)
        return
      }
      const span = view.x1 - view.x0
      const idxFloat = view.x0 + ((px - left) / plotW) * span
      const index = Math.round(clamp(idxFloat, 0, Math.max(0, maxIndex)))

      let best: TooltipState | null = null
      let bestDist = 28

      series.forEach((s) => {
        if (hiddenIds.has(s.id)) return
        const v = s.values[index]
        if (v == null) return
        const cx = xScale(index)
        const cy = yScale(v)
        const dist = Math.hypot(px - cx, py - cy)
        if (dist < bestDist) {
          bestDist = dist
          best = {
            x: px,
            y: py,
            index,
            seriesId: s.id,
            value: v,
            seriesName: s.name,
          }
        }
      })

      onHover(best)
    },
    [
      isPanning,
      left,
      plotW,
      plotH,
      top,
      view.x0,
      view.x1,
      series,
      hiddenIds,
      xScale,
      yScale,
      onHover,
      maxIndex,
    ],
  )

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      className="block select-none text-slate-500 dark:text-slate-400"
      style={{ cursor: isPanning ? 'grabbing' : enableZoom ? 'crosshair' : 'default' }}
      onMouseMove={(e) => {
        if (!isPanning) handlePointerMove(e.clientX, e.clientY)
      }}
      onMouseLeave={() => {
        onHover(null)
      }}
    >
      <defs>
        <clipPath id={clipId}>
          <rect x={left} y={top} width={plotW} height={plotH} />
        </clipPath>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path
            d="M 40 0 L 0 0 0 40"
            fill="none"
            className="stroke-slate-200 dark:stroke-slate-700"
            strokeWidth="0.5"
          />
        </pattern>
      </defs>
      <rect
        x={left}
        y={top}
        width={plotW}
        height={plotH}
        fill="url(#grid)"
        className="stroke-slate-300 dark:stroke-slate-600"
        strokeWidth="1"
      />

      {yTicks.map((t) => {
        const y = yScale(t)
        return (
          <g key={t}>
            <line
              x1={left}
              y1={y}
              x2={left + plotW}
              y2={y}
              className="stroke-slate-200 dark:stroke-slate-700"
              strokeWidth="1"
              strokeDasharray="4 4"
            />
            <text
              x={left - 8}
              y={y}
              textAnchor="end"
              dominantBaseline="middle"
              className="fill-slate-600 text-[10px] dark:fill-slate-400"
            >
              {formatTick(t)}
            </text>
          </g>
        )
      })}

      {xTicks.map((t) => {
        const x = xScale(t)
        return (
          <g key={t}>
            <line
              x1={x}
              y1={top}
              x2={x}
              y2={top + plotH}
              className="stroke-slate-200 dark:stroke-slate-700"
              strokeWidth="1"
              strokeDasharray="4 4"
            />
            <text
              x={x}
              y={top + plotH + 18}
              textAnchor="middle"
              className="fill-slate-600 text-[10px] dark:fill-slate-400"
            >
              {Number.isInteger(t) ? t : t.toFixed(1)}
            </text>
          </g>
        )
      })}

      <g clipPath={`url(#${clipId})`}>
        {showAreaFill &&
          series.map((s, sIdx) => {
            if (hiddenIds.has(s.id)) return null
            const color = getSeriesColor(sIdx, s.color)
            const segments = splitSegments(s.values)
            return segments.map((seg, segIdx) => {
              const pts = seg.map((p) => ({ x: xScale(p.i), y: yScale(p.v) }))
              const lineD = pts.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${pt.x} ${pt.y}`).join(' ')
              const x0 = pts[0].x
              const x1 = pts[pts.length - 1].x
              const areaD = `${lineD} L ${x1} ${plotBottom} L ${x0} ${plotBottom} Z`
              return (
                <path
                  key={`area-${s.id}-${segIdx}`}
                  d={areaD}
                  fill={color}
                  fillOpacity={areaOpacity}
                  stroke="none"
                />
              )
            })
          })}
        {series.map((s, sIdx) => {
          if (hiddenIds.has(s.id)) return null
          const color = getSeriesColor(sIdx, s.color)
          const segments = splitSegments(s.values)
          return segments.map((seg, segIdx) => {
            const d = seg
              .map((p, i) => {
                const x = xScale(p.i)
                const y = yScale(p.v)
                return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
              })
              .join(' ')
            return (
              <path
                key={`${s.id}-${segIdx}`}
                d={d}
                fill="none"
                stroke={color}
                strokeWidth={lineStroke}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            )
          })
        })}
      </g>
    </svg>
  )
}
