import type { TooltipState } from './types'

interface TooltipProps {
  state: TooltipState
  containerWidth: number
  containerHeight: number
}

export function ChartTooltip({ state, containerWidth, containerHeight }: TooltipProps) {
  const pad = 8
  let left = state.x + pad
  let top = state.y - 40
  const boxW = 160
  const boxH = 56
  if (left + boxW > containerWidth - pad) left = state.x - boxW - pad
  if (top < pad) top = state.y + pad
  if (top + boxH > containerHeight - pad) top = containerHeight - boxH - pad

  return (
    <div
      className="pointer-events-none absolute z-10 rounded-md border border-slate-200 bg-white px-2 py-1.5 text-xs shadow-lg dark:border-slate-600 dark:bg-slate-800"
      style={{ left, top, minWidth: boxW }}
      role="tooltip"
    >
      <div className="font-medium text-slate-900 dark:text-slate-100">{state.seriesName}</div>
      <div className="text-slate-600 dark:text-slate-300">
        Index: <span className="font-mono">{state.index}</span>
      </div>
      <div className="text-slate-600 dark:text-slate-300">
        Value: <span className="font-mono">{state.value.toFixed(3)}</span>
      </div>
    </div>
  )
}
