# graphs-vite-app

Автономное приложение на **Vite + React + TypeScript + Tailwind**: страница **Graphs** (временные ряды) вынесена из основного `ui-app`.

## Требования

- Node.js **18+** (рекомендуется 20+)
- npm

## Запуск для разработки

```bash
cd graphs-vite-app
npm install
npm run dev
```

Откройте в браузере адрес из терминала (по умолчанию **http://localhost:5174**).

## Сборка и предпросмотр продакшена

```bash
npm run build
npm run preview
```

Артефакты сборки — папка `dist/` (статика для nginx, S3, CDN и т.п.).

## Структура

| Путь | Описание |
|------|----------|
| `src/App.tsx` | Страница: заголовок, кнопка теней, `TimeSeriesChart` |
| `src/components/graphs/` | Копия модуля графиков (зум X/Y, легенда, фильтры, тестовые данные) |
| `src/components/ui/` | Минимальные `PageContainer`, `PageHeader`, `Button` |

При изменениях графиков в основном проекте скопируйте папку заново:

```bash
# из корня cursor_test (Windows PowerShell)
Copy-Item -Path "ui-app\src\components\graphs" -Destination "graphs-vite-app\src\components\graphs" -Recurse -Force
```

## Порт

Порт задаётся в `package.json` (`dev` / `preview`: **5174**), при необходимости измените флаг `--port`.
