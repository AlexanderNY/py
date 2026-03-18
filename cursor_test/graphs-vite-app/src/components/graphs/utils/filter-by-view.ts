import type { TimeSeries, ViewWindow } from '../types'

export function getIndexRange(view: ViewWindow, pointCount: number): { i0: number; i1: number } {
  if (pointCount <= 0) return { i0: 0, i1: 0 }
  const a = Math.max(0, Math.floor(view.x0))
  const b = Math.min(pointCount - 1, Math.ceil(view.x1))
  return { i0: Math.min(a, b), i1: Math.max(a, b) }
}

/** Скрыть ряды без null на [i0, i1] */
export function hiddenIdsGapsOnly(data: TimeSeries[], i0: number, i1: number): Set<string> {
  const hide = new Set<string>()
  for (const s of data) {
    let hasNull = false
    for (let i = i0; i <= i1; i++) {
      if (s.values[i] === null) {
        hasNull = true
        break
      }
    }
    if (!hasNull) hide.add(s.id)
  }
  return hide
}

interface StatRow {
  id: string
  v: number
}

/** Оставить только 3 ряда с наименьшим локальным минимумом на интервале */
export function hiddenIdsTop3Min(data: TimeSeries[], i0: number, i1: number): Set<string> {
  const rows: StatRow[] = []
  for (const s of data) {
    let min = Number.POSITIVE_INFINITY
    for (let i = i0; i <= i1; i++) {
      const val = s.values[i]
      if (val != null && Number.isFinite(val)) min = Math.min(min, val)
    }
    if (Number.isFinite(min)) rows.push({ id: s.id, v: min })
  }
  rows.sort((a, b) => a.v - b.v || a.id.localeCompare(b.id))
  const keep = new Set(rows.slice(0, Math.min(3, rows.length)).map((r) => r.id))
  const hide = new Set<string>()
  for (const s of data) {
    if (!keep.has(s.id)) hide.add(s.id)
  }
  return hide
}

/** Оставить только 3 ряда с наибольшим локальным максимумом на интервале */
export function hiddenIdsTop3Max(data: TimeSeries[], i0: number, i1: number): Set<string> {
  const rows: StatRow[] = []
  for (const s of data) {
    let max = Number.NEGATIVE_INFINITY
    for (let i = i0; i <= i1; i++) {
      const val = s.values[i]
      if (val != null && Number.isFinite(val)) max = Math.max(max, val)
    }
    if (Number.isFinite(max)) rows.push({ id: s.id, v: max })
  }
  rows.sort((a, b) => b.v - a.v || a.id.localeCompare(b.id))
  const keep = new Set(rows.slice(0, Math.min(3, rows.length)).map((r) => r.id))
  const hide = new Set<string>()
  for (const s of data) {
    if (!keep.has(s.id)) hide.add(s.id)
  }
  return hide
}
