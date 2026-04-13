import { useAuth } from '@/contexts/auth-context'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'

export function BillingTabContent() {
  const { user } = useAuth()

  return (
    <Card className="animate-slide-up">
      <CardHeader>
        <CardTitle>Current plan</CardTitle>
        <CardDescription>Your active tariff and subscription</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between items-center py-3 border-b border-[var(--border-color)]">
          <span className="text-[var(--text-secondary)]">Tariff</span>
          <span className="font-medium capitalize">{user?.tariff ?? 'free'}</span>
        </div>
        <p className="text-sm text-[var(--text-muted)] mt-4">
          Billing and plan management will be available here.
        </p>
      </CardContent>
    </Card>
  )
}
