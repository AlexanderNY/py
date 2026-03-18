import type { TimeSeries } from '../types'
import { getSeriesColor } from './colors'

const SERIES_COUNT = 60
const POINTS = 120
/** Разрывы только у рядов с индексами ≥11 (не трогаем спец. ряды 1–11) */
const SERIES_INDICES_WITH_GAPS = new Set([14, 19, 24, 34, 44, 54])
const NULL_FRACTION = 0.12

const HIGH_COUNT = 5
const SMALL_COUNT = 5
const RAMP_INDEX = HIGH_COUNT + SMALL_COUNT // 10 — один ряд 0→40

function seededRandom(seed: number): () => number {
  let s = seed % 2147483647
  if (s <= 0) s += 2147483646
  return () => {
    s = (s * 16807) % 2147483647
    return (s - 1) / 2147483646
  }
}

function clamp(v: number, lo: number, hi: number): number {
  return Math.min(hi, Math.max(lo, v))
}

function seriesName(s: number): string {
  if (s < HIGH_COUNT) return `>1000 · ${s + 1}`
  if (s < RAMP_INDEX) return `−1…1 · ${s - HIGH_COUNT + 1}`
  if (s === RAMP_INDEX) return `0 → 40`
  return `Series ${s + 1}`
}

export function generateTestTimeSeries(): TimeSeries[] {
  const series: TimeSeries[] = []
  for (let s = 0; s < SERIES_COUNT; s++) {
    const rand = seededRandom(1000 + s * 97)
    const values: (number | null)[] = []
    const allowGaps = SERIES_INDICES_WITH_GAPS.has(s)

    if (s < HIGH_COUNT) {
      const phase = rand() * Math.PI * 2
      const freq = 0.06 + rand() * 0.1
      const base = 1800 + s * 120
      const swing = 80 + rand() * 120
      for (let i = 0; i < POINTS; i++) {
        if (allowGaps && rand() < NULL_FRACTION) {
          values.push(null)
          continue
        }
        const noise = (rand() - 0.5) * 25
        const v = base + swing * Math.sin(i * freq + phase) + noise
        values.push(Math.max(1000.01, v))
      }
    } else if (s < RAMP_INDEX) {
      const phase = rand() * Math.PI * 2
      const f1 = 0.1 + rand() * 0.12
      const f2 = 0.05 + rand() * 0.08
      for (let i = 0; i < POINTS; i++) {
        if (allowGaps && rand() < NULL_FRACTION) {
          values.push(null)
          continue
        }
        let v =
          0.88 * Math.sin(i * f1 + phase) * Math.cos(i * f2 + phase * 0.7) +
          (rand() - 0.5) * 0.08
        v = clamp(v, -1, 1)
        values.push(v)
      }
    } else if (s === RAMP_INDEX) {
      const last = POINTS - 1
      for (let i = 0; i < POINTS; i++) {
        values.push((40 * i) / last)
      }
    } else {
      const phase = rand() * Math.PI * 2
      const freq = 0.08 + rand() * 0.15
      const amp = 15 + rand() * 25
      const offset = rand() * 40 - 20
      for (let i = 0; i < POINTS; i++) {
        if (allowGaps && rand() < NULL_FRACTION) {
          values.push(null)
          continue
        }
        const t = i * freq + phase
        const noise = (rand() - 0.5) * 4
        values.push(offset + amp * Math.sin(t) + noise)
      }
    }

    series.push({
      id: `series-${s + 1}`,
      name: seriesName(s),
      values,
      color: getSeriesColor(s),
    })
  }
  return series
}
