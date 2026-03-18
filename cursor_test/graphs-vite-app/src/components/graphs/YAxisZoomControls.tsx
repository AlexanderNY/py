interface YAxisZoomControlsProps {
  onZoomInY: () => void
  onZoomOutY: () => void
  onResetY: () => void
  isYManual: boolean
}

export function YAxisZoomControls({
  onZoomInY,
  onZoomOutY,
  onResetY,
  isYManual,
}: YAxisZoomControlsProps) {
  const btn =
    'rounded-md border border-slate-300 bg-white px-2 py-1 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-40 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700'

  return (
    <div className="flex flex-wrap items-center gap-2 border-t border-slate-200 pt-2 dark:border-slate-700">
      <span className="text-xs font-medium text-slate-600 dark:text-slate-300">Ось Y:</span>
      <button type="button" className={btn} onClick={onZoomInY} aria-label="Y zoom in">
        Y+
      </button>
      <button type="button" className={btn} onClick={onZoomOutY} aria-label="Y zoom out">
        Y−
      </button>
      <button type="button" className={btn} onClick={onResetY} aria-label="Y auto">
        Y сброс
      </button>
      <span
        className={`text-xs ${isYManual ? 'text-amber-600 dark:text-amber-400' : 'text-slate-500 dark:text-slate-400'}`}
      >
        {isYManual ? 'Y: вручную' : 'Y: авто'}
      </span>
    </div>
  )
}
