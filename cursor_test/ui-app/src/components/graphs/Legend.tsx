import type { TimeSeries } from './types'
import { getSeriesColor } from './utils/colors'

interface LegendProps {
  series: TimeSeries[]
  hiddenIds: ReadonlySet<string>
  onToggle: (id: string) => void
  onShowAll: () => void
  onHideAll: () => void
  /** Легенда только для просмотра, пока активен фильтр по интервалу */
  filterActive?: boolean
}

function EyeIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

function EyeOffIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  )
}

const bulkBtn =
  'flex-1 rounded-md border border-slate-300 bg-white px-2 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700'

export function Legend({
  series,
  hiddenIds,
  onToggle,
  onShowAll,
  onHideAll,
  filterActive = false,
}: LegendProps) {
  return (
    <div
      className="max-h-[min(70vh,28rem)] overflow-y-auto rounded-lg border border-slate-200 bg-slate-50/80 p-2 dark:border-slate-700 dark:bg-slate-900/50"
      role="list"
      aria-label="Chart series legend"
    >
      <div className="mb-2 flex gap-2">
        <button
          type="button"
          className={bulkBtn}
          disabled={filterActive}
          onClick={onShowAll}
          title={filterActive ? 'Сначала отключите фильтр («Все графики»)' : undefined}
        >
          Включить все
        </button>
        <button
          type="button"
          className={bulkBtn}
          disabled={filterActive}
          onClick={onHideAll}
          title={filterActive ? 'Сначала отключите фильтр («Все графики»)' : undefined}
        >
          Выключить все
        </button>
      </div>
      {filterActive && (
        <p className="mb-2 rounded-md bg-amber-500/10 px-2 py-1 text-xs text-amber-800 dark:text-amber-200">
          Легенда заблокирована. Нажмите «Все графики», чтобы снова включать/выключать ряды вручную.
        </p>
      )}
      <ul className="flex flex-col gap-1 text-sm">
        {series.map((s, idx) => {
          const visible = !hiddenIds.has(s.id)
          const color = getSeriesColor(idx, s.color)
          return (
            <li key={s.id}>
              <button
                type="button"
                disabled={filterActive}
                onClick={() => onToggle(s.id)}
                className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left transition hover:bg-slate-200/80 disabled:cursor-not-allowed disabled:opacity-60 dark:hover:bg-slate-800"
                aria-pressed={visible}
                aria-label={visible ? `Hide ${s.name}` : `Show ${s.name}`}
              >
                <span
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded border border-slate-300 bg-white text-slate-600 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300"
                  title={visible ? 'Click to hide' : 'Click to show'}
                >
                  {visible ? (
                    <EyeIcon />
                  ) : (
                    <EyeOffIcon className="opacity-60" />
                  )}
                </span>
                <span
                  className="h-3 w-3 shrink-0 rounded-full ring-1 ring-black/10 dark:ring-white/20"
                  style={{ backgroundColor: color, opacity: visible ? 1 : 0.35 }}
                />
                <span
                  className={`min-w-0 flex-1 truncate ${
                    visible ? '' : 'text-slate-500 line-through dark:text-slate-400'
                  }`}
                >
                  {s.name}
                </span>
              </button>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
