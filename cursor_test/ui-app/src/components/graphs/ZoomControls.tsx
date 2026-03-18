interface ZoomControlsProps {
  onZoomIn: () => void
  onZoomOut: () => void
  onReset: () => void
  disabled?: boolean
}

export function ZoomControls({
  onZoomIn,
  onZoomOut,
  onReset,
  disabled = false,
}: ZoomControlsProps) {
  const btn =
    'rounded-md border border-slate-300 bg-white px-2 py-1 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-40 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700'

  return (
    <div className="flex flex-wrap items-center gap-2">
      <button type="button" className={btn} onClick={onZoomIn} disabled={disabled} aria-label="Zoom in">
        +
      </button>
      <button type="button" className={btn} onClick={onZoomOut} disabled={disabled} aria-label="Zoom out">
        −
      </button>
      <button type="button" className={btn} onClick={onReset} disabled={disabled} aria-label="Reset zoom">
        Reset
      </button>
    </div>
  )
}
