import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'

export function WordPressPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">WordPress Integration</h1>
        <p className="text-[var(--text-secondary)] mt-1">Manage your WordPress sites and content</p>
      </div>

      <Card className="animate-slide-up">
        <CardHeader className="text-center">
          <div className="mx-auto w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-primary-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M21.469 6.825c.84 1.537 1.318 3.3 1.318 5.175 0 3.979-2.156 7.456-5.363 9.325l3.295-9.527c.615-1.54.82-2.771.82-3.864 0-.405-.026-.78-.07-1.11m-7.981.105c.647-.034 1.232-.1 1.232-.1.582-.075.514-.93-.067-.899 0 0-1.755.138-2.885.138-1.063 0-2.855-.138-2.855-.138-.581-.031-.649.857-.068.899 0 0 .548.066 1.13.1l1.681 4.605-2.36 7.076-3.929-11.68c.65-.034 1.234-.1 1.234-.1.581-.075.514-.93-.068-.899 0 0-1.754.138-2.885.138-.202 0-.44-.006-.692-.014C5.644 3.404 8.577 1.214 12 1.214c2.55 0 4.87.975 6.607 2.57-.042-.003-.084-.007-.127-.007-.961 0-1.644.842-1.644 1.745 0 .811.467 1.497.967 2.308.374.65.811 1.482.811 2.687 0 .834-.32 1.8-.748 3.146l-.98 3.275-3.55-10.567zm-4.39 16.307c-1.354-.46-2.576-1.17-3.615-2.078l3.042-8.828 3.115 8.533c.02.05.046.095.072.138-1.32.56-2.77.87-4.287.87-.442 0-.877-.028-1.305-.082m-1.885-.906C4.001 20.054 1.214 16.303 1.214 12c0-1.628.367-3.17 1.022-4.547l5.627 15.418c.03.082.063.162.099.24-.015-.005-.03-.01-.045-.016l-.003-.001z"/>
            </svg>
          </div>
          <CardTitle className="text-2xl">Coming Soon</CardTitle>
          <CardDescription>
            WordPress integration features are currently under development
          </CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          <p className="text-[var(--text-muted)]">
            This section will allow you to:
          </p>
          <ul className="mt-4 space-y-2 text-[var(--text-secondary)]">
            <li className="flex items-center justify-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Connect WordPress sites
            </li>
            <li className="flex items-center justify-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Auto-publish content
            </li>
            <li className="flex items-center justify-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Manage posts and media
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}


