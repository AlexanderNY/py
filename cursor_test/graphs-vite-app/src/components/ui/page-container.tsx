import type { ReactNode } from 'react'

interface PageContainerProps {
  children: ReactNode
  maxWidth?: 'default' | 'wide'
  className?: string
}

export function PageContainer({
  children,
  maxWidth = 'default',
  className = '',
}: PageContainerProps) {
  const mw = maxWidth === 'wide' ? 'max-w-6xl' : 'max-w-4xl'
  return (
    <div className={`mx-auto space-y-6 animate-fade-in px-4 py-8 ${mw} ${className}`.trim()}>
      {children}
    </div>
  )
}
