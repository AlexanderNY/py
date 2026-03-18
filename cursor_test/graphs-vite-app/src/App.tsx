import { useMemo, useState } from 'react'
import { PageContainer, PageHeader, Button } from '@/components/ui'
import { TimeSeriesChart, generateTestTimeSeries } from '@/components/graphs'

export default function App() {
  const data = useMemo(() => generateTestTimeSeries(), [])
  const [showShadows, setShowShadows] = useState(true)

  return (
    <PageContainer maxWidth="wide">
      <PageHeader
        title="Graphs"
        description="60×120 точек. Фильтры по X, зум X/Y, легенда. Автономное демо (graphs-vite-app)."
      />
      <div className="flex flex-wrap items-center gap-2">
        <Button type="button" variant="secondary" size="sm" onClick={() => setShowShadows((v) => !v)}>
          {showShadows ? 'Отключить тени' : 'Включить тени'}
        </Button>
      </div>
      <TimeSeriesChart
        data={data}
        height={440}
        showLegend
        enableZoom
        showAreaFill={showShadows}
      />
    </PageContainer>
  )
}
