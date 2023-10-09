import { posthog } from 'posthog-js'
import { useUser } from '@auth0/nextjs-auth0/client'
import { useRouter } from 'next/router'
import { FC, ReactNode, useEffect } from 'react'
import { User } from '@/models/api'
import { PostHogProvider } from 'posthog-js/react'
import { POSTHOG_HOST, POSTHOG_KEY } from '@/config'

type WithAnalyticsProps = {
  children: ReactNode
}

const WithAnalytics: FC<WithAnalyticsProps> = ({ children }) => {
  const router = useRouter()
  const { user: authUser, error } = useUser()
  const user = authUser as User

  // Check that PostHog is client-side (used to handle Next.js SSR)
  if (typeof window !== 'undefined') {
    posthog.init(POSTHOG_KEY || '', {
      api_host: POSTHOG_HOST || 'https://app.posthog.com',
      // Enable debug mode in development
      loaded: (posthog) => {
        if (process.env.NODE_ENV === 'development') posthog.debug()
      },
      capture_pageview: false, // Disable automatic pageview capture, as we capture manually
    })
  }

  useEffect(() => {
    if (error) {
      console.error('Error fetching user:', error)
      return
    }
    if (user && user.email) {
      posthog.identify(user.email, {
        email: user.email,
        name: user.name,
        organization_name: user.organization.name,
      })
    }
  }, [user, error, router])

  return <PostHogProvider>{children}</PostHogProvider>
}

export default WithAnalytics
