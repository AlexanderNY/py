import { useCallback, useMemo, useState } from 'react'
import { clamp } from '../utils/scales'
import type { ViewWindow } from '../types'

const MIN_SPAN = 4
const ZOOM_FACTOR = 1.15

export function useZoom(pointCount: number) {
  const dataMaxIdx = Math.max(0, pointCount - 1)
  /** Right edge of x domain (single-point series uses 0..1 for visible span) */
  const axisMax = dataMaxIdx >= 1 ? dataMaxIdx : 1

  const initial = useMemo<ViewWindow>(
    () => ({ x0: 0, x1: axisMax }),
    [axisMax],
  )

  const [view, setView] = useState<ViewWindow>(initial)

  const reset = useCallback(() => {
    setView({ x0: 0, x1: axisMax })
  }, [axisMax])

  const zoomAt = useCallback(
    (relX: number, deltaY: number) => {
      if (pointCount <= 1 && dataMaxIdx <= 0) return
      const { x0, x1 } = view
      const span = Math.max(x1 - x0, 1e-9)
      const anchor = x0 + clamp(relX, 0, 1) * span
      const factor = deltaY > 0 ? ZOOM_FACTOR : 1 / ZOOM_FACTOR
      let newSpan = span * factor
      const maxSpan = axisMax + 1e-6
      newSpan = clamp(newSpan, MIN_SPAN, maxSpan)
      const left = anchor - clamp(relX, 0, 1) * newSpan
      let nx0 = left
      let nx1 = left + newSpan
      if (nx0 < 0) {
        nx1 -= nx0
        nx0 = 0
      }
      if (nx1 > axisMax) {
        const over = nx1 - axisMax
        nx0 -= over
        nx1 = axisMax
        if (nx0 < 0) nx0 = 0
      }
      if (nx1 - nx0 < MIN_SPAN) {
        const mid = (nx0 + nx1) / 2
        nx0 = clamp(mid - MIN_SPAN / 2, 0, axisMax - MIN_SPAN)
        nx1 = nx0 + MIN_SPAN
      }
      setView({ x0: nx0, x1: nx1 })
    },
    [view, axisMax, pointCount, dataMaxIdx],
  )

  const panByPixels = useCallback(
    (deltaPx: number, plotWidth: number) => {
      if (plotWidth <= 0) return
      const { x0, x1 } = view
      const span = x1 - x0
      const dataPerPx = span / plotWidth
      const shift = -deltaPx * dataPerPx
      let nx0 = x0 + shift
      let nx1 = x1 + shift
      if (nx0 < 0) {
        nx1 -= nx0
        nx0 = 0
      }
      if (nx1 > axisMax) {
        const over = nx1 - axisMax
        nx0 -= over
        nx1 = axisMax
        if (nx0 < 0) nx0 = 0
      }
      setView({ x0: nx0, x1: nx1 })
    },
    [view, axisMax],
  )

  const zoomIn = useCallback(() => {
    zoomAt(0.5, 1)
  }, [zoomAt])

  const zoomOut = useCallback(() => {
    zoomAt(0.5, -1)
  }, [zoomAt])

  return {
    view,
    setView,
    reset,
    zoomAt,
    panByPixels,
    zoomIn,
    zoomOut,
    axisMax,
    dataMaxIdx,
  }
}
