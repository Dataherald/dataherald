import { POSTHOG_DISABLED, POSTHOG_HOST, POSTHOG_KEY } from '@/config'
import { useAppContext } from '@/contexts/app-context'
import { posthog } from 'posthog-js'
import { PostHogProvider } from 'posthog-js/react'
import { FC, ReactNode, useEffect } from 'react'

type WithAnalyticsProps = {
  children: ReactNode
}

const WithAnalytics: FC<WithAnalyticsProps> = ({ children }) => {
  const { user, organization } = useAppContext()

  // Check that PostHog is client-side (used to handle Next.js SSR)
  if (!POSTHOG_DISABLED && typeof window !== 'undefined') {
    posthog.init(POSTHOG_KEY || '', {
      api_host: POSTHOG_HOST || 'https://app.posthog.com',
      // Enable debug mode in development
      loaded: (posthog) => {
        if (process.env.NODE_ENV === 'development') posthog.debug()
      },
    })
  }

  useEffect(() => {
    if (POSTHOG_DISABLED || !user || !organization) return
    if (user.email) {
      posthog.identify(user.email, {
        email: user.email,
        name: user.name,
        organization_name: organization.name,
      })
    }
  }, [organization, user])

  return !POSTHOG_DISABLED ? (
    <PostHogProvider>{children}</PostHogProvider>
  ) : (
    children
  )
}

export default WithAnalytics
