interface ChartInstructionsProps {
  enableZoom: boolean
}

export function ChartInstructions({ enableZoom }: ChartInstructionsProps) {
  if (!enableZoom) return null

  return (
    <div
      className="mt-3 rounded-lg border border-slate-200 bg-slate-50/80 px-3 py-2.5 text-xs leading-relaxed text-slate-600 dark:border-slate-700 dark:bg-slate-900/40 dark:text-slate-400"
      aria-label="Инструкция по графику"
    >
      <ul className="list-inside list-disc space-y-1 marker:text-slate-400 dark:marker:text-slate-500">
        <li>
          <span className="font-medium text-slate-700 dark:text-slate-300">Ось X:</span> колесо мыши — масштаб;
          перетаскивание — панорама. Кнопки +, −, Reset.
        </li>
        <li>
          <span className="font-medium text-slate-700 dark:text-slate-300">Ось Y:</span>{' '}
          <kbd className="rounded border border-slate-300 bg-white px-1 font-mono dark:border-slate-600 dark:bg-slate-800">
            Shift
          </kbd>{' '}
          + колесо — масштаб по Y;{' '}
          <kbd className="rounded border border-slate-300 bg-white px-1 font-mono dark:border-slate-600 dark:bg-slate-800">
            Shift
          </kbd>{' '}
          + перетаскивание — панорама по Y. Y+, Y−, «Y сброс» — ручной зум и возврат к авто-масштабу.
        </li>
        <li>
          <span className="font-medium text-slate-700 dark:text-slate-300">Фильтры</span> (разрывы, минимумы,
          максимумы) считаются по <strong>видимому сейчас отрезку по X</strong> (после зума/панорамы).
        </li>
        <li>
          Наведение на линию — подсказка со значением. В легенде — «Включить все» / «Выключить все» и
          показ/скрытие каждого ряда (при режиме «Все графики»).
        </li>
      </ul>
    </div>
  )
}
