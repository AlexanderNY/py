import { useCallback, useState } from 'react'
import { clamp } from '../utils/scales'

const Y_ZOOM_FACTOR = 1.15

function ensureSpan(min: number, max: number): { min: number; max: number } {
  if (!Number.isFinite(min) || !Number.isFinite(max)) return { min: 0, max: 1 }
  if (max <= min) {
    const p = Math.abs(min) * 0.05 || 0.5
    return { min: min - p, max: max + p }
  }
  return { min, max }
}

export function useYZoom() {
  const [manual, setManual] = useState<{ min: number; max: number } | null>(null)

  const resetY = useCallback(() => {
    setManual(null)
  }, [])

  const zoomYAt = useCallback((relY: number, deltaY: number, yAutoMin: number, yAutoMax: number) => {
    setManual((prev) => {
      const base = prev ?? ensureSpan(yAutoMin, yAutoMax)
      let { min: yMin, max: yMax } = base
      let span = yMax - yMin
      if (span <= 0) span = 1
      const ry = clamp(relY, 0, 1)
      const anchor = yMin + ry * span
      const factor = deltaY > 0 ? Y_ZOOM_FACTOR : 1 / Y_ZOOM_FACTOR
      let newSpan = span * factor
      const minSpan = Math.max(span * 0.015, Math.abs(anchor) * 1e-9, 1e-12)
      newSpan = Math.max(newSpan, minSpan)
      newSpan = Math.min(newSpan, span * 80)
      const left = anchor - ry * newSpan
      let nMin = left
      let nMax = left + newSpan
      const out = ensureSpan(nMin, nMax)
      return { min: out.min, max: out.max }
    })
  }, [])

  const panYByPixels = useCallback((deltaPy: number, plotH: number, yAutoMin: number, yAutoMax: number) => {
    if (plotH <= 0) return
    setManual((prev) => {
      const base = prev ?? ensureSpan(yAutoMin, yAutoMax)
      const { min: yMin, max: yMax } = base
      const span = Math.max(yMax - yMin, 1e-12)
      const shift = (deltaPy / plotH) * span
      return { min: yMin - shift, max: yMax - shift }
    })
  }, [])

  const zoomYIn = useCallback((yAutoMin: number, yAutoMax: number) => {
    zoomYAt(0.5, 1, yAutoMin, yAutoMax)
  }, [zoomYAt])

  const zoomYOut = useCallback((yAutoMin: number, yAutoMax: number) => {
    zoomYAt(0.5, -1, yAutoMin, yAutoMax)
  }, [zoomYAt])

  return {
    manualY: manual,
    resetY,
    zoomYAt,
    panYByPixels,
    zoomYIn,
    zoomYOut,
  }
}
