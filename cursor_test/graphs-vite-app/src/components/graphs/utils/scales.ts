export function linearScale(
  domain: [number, number],
  range: [number, number],
): (value: number) => number {
  const [d0, d1] = domain
  const [r0, r1] = range
  const span = d1 - d0
  if (span === 0) {
    return () => (r0 + r1) / 2
  }
  return (value: number) => r0 + ((value - d0) / span) * (r1 - r0)
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value))
}

export interface YDomainResult {
  min: number
  max: number
}

const Y_PADDING_RATIO = 0.08

export function computeYDomain(
  seriesList: { values: (number | null)[]; visible: boolean }[],
  x0: number,
  x1: number,
  maxLen: number,
): YDomainResult {
  let min = Number.POSITIVE_INFINITY
  let max = Number.NEGATIVE_INFINITY
  const i0 = Math.max(0, Math.floor(x0))
  const i1 = Math.min(maxLen, Math.ceil(x1) + 1)

  for (const s of seriesList) {
    if (!s.visible) continue
    for (let i = i0; i < i1; i++) {
      const v = s.values[i]
      if (v == null || Number.isNaN(v)) continue
      min = Math.min(min, v)
      max = Math.max(max, v)
    }
  }

  if (!Number.isFinite(min) || !Number.isFinite(max)) {
    return { min: 0, max: 1 }
  }
  if (min === max) {
    const pad = Math.abs(min) * 0.1 || 0.5
    return { min: min - pad, max: max + pad }
  }
  const pad = (max - min) * Y_PADDING_RATIO
  return { min: min - pad, max: max + pad }
}
