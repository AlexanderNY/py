import { useAuth } from '@/contexts/auth-context'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'

export function BillingPage() {
  const { user } = useAuth()

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">Billing</h1>
        <p className="text-[var(--text-secondary)] mt-1">Your current plan and billing details</p>
      </div>

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
    </div>
  )
}
