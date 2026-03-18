interface PageHeaderProps {
  title: string
  description?: string
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div className="space-y-1">
      <h1 className="text-3xl font-bold text-[var(--text-primary)]">{title}</h1>
      {description != null && (
        <p className="mt-1 text-[var(--text-secondary)]">{description}</p>
      )}
    </div>
  )
}
