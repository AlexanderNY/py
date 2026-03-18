import { useCallback, useEffect, useMemo, useRef, useState, type RefObject } from 'react'
import type { TimeSeriesChartProps, TooltipState } from './types'
import { ChartCanvas } from './ChartCanvas'
import { ChartTooltip } from './Tooltip'
import { Legend } from './Legend'
import { ZoomControls } from './ZoomControls'
import { YAxisZoomControls } from './YAxisZoomControls'
import { ChartInstructions } from './ChartInstructions'
import { useChartDimensions } from './hooks/useChartDimensions'
import { useZoom } from './hooks/useZoom'
import { useYZoom } from './hooks/useYZoom'
import { CHART_MARGINS, getPlotSize } from './chart-margins'
import { clamp, computeYDomain } from './utils/scales'
import {
  getIndexRange,
  hiddenIdsGapsOnly,
  hiddenIdsTop3Max,
  hiddenIdsTop3Min,
} from './utils/filter-by-view'

export type SeriesViewFilter = 'all' | 'gaps' | 'min3' | 'max3'

export function TimeSeriesChart({
  data,
  height = 440,
  showLegend = true,
  enableZoom = true,
  showAreaFill = true,
  className = '',
}: TimeSeriesChartProps) {
  const [hiddenIds, setHiddenIds] = useState<Set<string>>(() => new Set())
  const [seriesFilter, setSeriesFilter] = useState<SeriesViewFilter>('all')
  const [tooltip, setTooltip] = useState<TooltipState | null>(null)
  const [isPanning, setIsPanning] = useState(false)
  const [isPanningY, setIsPanningY] = useState(false)
  const lastPanX = useRef(0)
  const lastPanY = useRef(0)

  const pointCount = useMemo(() => {
    if (!data.length) return 0
    return Math.max(...data.map((s) => s.values.length))
  }, [data])

  const dataMaxIdx = Math.max(0, pointCount - 1)
  const { ref, width } = useChartDimensions(900, height)
  const { plotW, plotH } = useMemo(() => getPlotSize(width, height), [width, height])

  const { view, reset, zoomAt, panByPixels, zoomIn, zoomOut } = useZoom(Math.max(pointCount, 1))
  const { manualY, resetY, zoomYAt, panYByPixels, zoomYIn, zoomYOut } = useYZoom()

  const yAuto = useMemo(
    () =>
      computeYDomain(
        data.map((s) => ({ values: s.values, visible: !hiddenIds.has(s.id) })),
        view.x0,
        view.x1,
        pointCount,
      ),
    [data, hiddenIds, view.x0, view.x1, pointCount],
  )

  const yMin = manualY?.min ?? yAuto.min
  const yMax = manualY?.max ?? yAuto.max

  useEffect(() => {
    reset()
    resetY()
  }, [pointCount, reset, resetY])

  useEffect(() => {
    if (seriesFilter === 'all') return
    const { i0, i1 } = getIndexRange(view, pointCount)
    if (seriesFilter === 'gaps') {
      setHiddenIds(hiddenIdsGapsOnly(data, i0, i1))
      return
    }
    if (seriesFilter === 'min3') {
      setHiddenIds(hiddenIdsTop3Min(data, i0, i1))
      return
    }
    if (seriesFilter === 'max3') {
      setHiddenIds(hiddenIdsTop3Max(data, i0, i1))
    }
  }, [seriesFilter, view.x0, view.x1, data, pointCount])

  const applyFilter = useCallback((mode: SeriesViewFilter) => {
    if (mode === 'all') {
      setSeriesFilter('all')
      setHiddenIds(new Set())
      return
    }
    setSeriesFilter(mode)
  }, [])

  useEffect(() => {
    if (!isPanning) return
    const onMove = (e: MouseEvent) => {
      panByPixels(e.clientX - lastPanX.current, plotW)
      lastPanX.current = e.clientX
    }
    const onUp = () => {
      setIsPanning(false)
      setTooltip(null)
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    return () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
  }, [isPanning, panByPixels, plotW])

  useEffect(() => {
    if (!isPanningY) return
    const onMove = (e: MouseEvent) => {
      panYByPixels(e.clientY - lastPanY.current, plotH, yAuto.min, yAuto.max)
      lastPanY.current = e.clientY
    }
    const onUp = () => {
      setIsPanningY(false)
      setTooltip(null)
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    return () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
  }, [isPanningY, panYByPixels, plotH, yAuto.min, yAuto.max])

  useEffect(() => {
    const el = ref.current
    if (!el || !enableZoom) return
    const handler = (e: WheelEvent) => {
      e.preventDefault()
      const r = el.getBoundingClientRect()
      const { plotW: pw, plotH: ph } = getPlotSize(width, height)
      const { left, top } = CHART_MARGINS
      if (e.shiftKey) {
        const py = e.clientY - r.top
        const relY = (top + ph - py) / Math.max(1, ph)
        zoomYAt(clamp(relY, 0, 1), e.deltaY, yAuto.min, yAuto.max)
      } else {
        if (pointCount < 2) return
        const rel = (e.clientX - r.left - left) / Math.max(1, pw)
        zoomAt(clamp(rel, 0, 1), e.deltaY)
      }
    }
    el.addEventListener('wheel', handler, { passive: false })
    return () => el.removeEventListener('wheel', handler)
  }, [enableZoom, zoomAt, zoomYAt, width, height, pointCount, yAuto.min, yAuto.max, ref])

  const toggleSeries = useCallback((id: string) => {
    setHiddenIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }, [])

  const showAllSeries = useCallback(() => {
    setSeriesFilter('all')
    setHiddenIds(new Set())
  }, [])

  const hideAllSeries = useCallback(() => {
    setSeriesFilter('all')
    setHiddenIds(new Set(data.map((s) => s.id)))
  }, [data])

  if (!data.length || pointCount === 0) {
    return (
      <div
        className={`rounded-lg border border-dashed border-slate-300 p-8 text-center text-slate-500 dark:border-slate-600 dark:text-slate-400 ${className}`}
      >
        No time series data
      </div>
    )
  }

  return (
    <div className={className}>
      <div className="mb-3 flex flex-col gap-2">
        {enableZoom && (
          <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-2 dark:border-slate-700 dark:bg-slate-900/30">
            <ZoomControls
              onZoomIn={zoomIn}
              onZoomOut={zoomOut}
              onReset={reset}
              disabled={pointCount < 2}
            />
            <YAxisZoomControls
              onZoomInY={() => zoomYIn(yAuto.min, yAuto.max)}
              onZoomOutY={() => zoomYOut(yAuto.min, yAuto.max)}
              onResetY={resetY}
              isYManual={manualY != null}
            />
          </div>
        )}
        <div className="flex flex-wrap items-center gap-2">
          <span className="w-full text-xs text-slate-500 dark:text-slate-400 sm:w-auto">
            Фильтр по видимому интервалу:
          </span>
          <button
            type="button"
            onClick={() => applyFilter('all')}
            className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition ${
              seriesFilter === 'all'
                ? 'border-primary-500 bg-primary-500/15 text-primary-700 dark:text-primary-300'
                : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700'
            }`}
          >
            Все графики
          </button>
          <button
            type="button"
            onClick={() => applyFilter('gaps')}
            className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition ${
              seriesFilter === 'gaps'
                ? 'border-primary-500 bg-primary-500/15 text-primary-700 dark:text-primary-300'
                : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700'
            }`}
          >
            Графики с разрывами
          </button>
          <button
            type="button"
            onClick={() => applyFilter('min3')}
            className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition ${
              seriesFilter === 'min3'
                ? 'border-primary-500 bg-primary-500/15 text-primary-700 dark:text-primary-300'
                : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700'
            }`}
          >
            Графики с минимальными значениями
          </button>
          <button
            type="button"
            onClick={() => applyFilter('max3')}
            className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition ${
              seriesFilter === 'max3'
                ? 'border-primary-500 bg-primary-500/15 text-primary-700 dark:text-primary-300'
                : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700'
            }`}
          >
            Графики с максимальными значениями
          </button>
        </div>
      </div>
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start">
        <div
          ref={ref as RefObject<HTMLDivElement>}
          className="relative min-h-[200px] min-w-0 flex-1 overflow-hidden rounded-lg border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-950"
          style={{
            height,
            cursor: isPanningY ? 'ns-resize' : isPanning ? 'grabbing' : enableZoom ? 'crosshair' : 'default',
          }}
          onMouseDown={(e) => {
            if (!enableZoom || e.button !== 0) return
            const t = e.target as HTMLElement
            if (t.closest('button')) return
            if (e.shiftKey) {
              setIsPanningY(true)
              lastPanY.current = e.clientY
              setTooltip(null)
              return
            }
            if (pointCount < 2) return
            setIsPanning(true)
            lastPanX.current = e.clientX
            setTooltip(null)
          }}
        >
          <ChartCanvas
            width={Math.max(width, 320)}
            height={height}
            series={data}
            hiddenIds={hiddenIds}
            view={view}
            yMin={yMin}
            yMax={yMax}
            onHover={setTooltip}
            isPanning={isPanning || isPanningY}
            enableZoom={enableZoom}
            maxIndex={dataMaxIdx}
            showAreaFill={showAreaFill}
          />
          {tooltip && !isPanning && !isPanningY && (
            <ChartTooltip
              state={tooltip}
              containerWidth={Math.max(width, 320)}
              containerHeight={height}
            />
          )}
        </div>
        {showLegend && (
          <div className="w-full shrink-0 lg:w-64 xl:w-72">
            <Legend
              series={data}
              hiddenIds={hiddenIds}
              onToggle={toggleSeries}
              onShowAll={showAllSeries}
              onHideAll={hideAllSeries}
              filterActive={seriesFilter !== 'all'}
            />
          </div>
        )}
      </div>
      <ChartInstructions enableZoom={enableZoom} />
    </div>
  )
}
