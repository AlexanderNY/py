import { useCallback, useEffect, useRef, useState, type RefObject } from 'react'

export interface ChartDimensions {
  width: number
  height: number
}

export function useChartDimensions(
  defaultWidth: number,
  defaultHeight: number,
): {
  ref: RefObject<HTMLDivElement | null>
  width: number
  height: number
} {
  const ref = useRef<HTMLDivElement>(null)
  const [width, setWidth] = useState(defaultWidth)
  const [height] = useState(defaultHeight)

  const measure = useCallback(() => {
    const el = ref.current
    if (!el) return
    const w = el.getBoundingClientRect().width
    if (w > 0) setWidth(Math.floor(w))
  }, [])

  useEffect(() => {
    measure()
    const el = ref.current
    if (!el) return
    const ro = new ResizeObserver(() => measure())
    ro.observe(el)
    return () => ro.disconnect()
  }, [measure])

  return { ref, width, height }
}
