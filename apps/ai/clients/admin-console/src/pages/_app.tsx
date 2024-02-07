import WithAnalytics from '@/components/hoc/WithAnalytics'
import WithSubscription from '@/components/hoc/WithSubscription'
import { AppContextProvider } from '@/contexts/app-context'
import { AuthProvider } from '@/contexts/auth-context'
import { SubscriptionProvider } from '@/contexts/subscription-context'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { cn } from '@/lib/utils'
import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { Lato, Source_Code_Pro } from 'next/font/google'
import { FC, ReactNode } from 'react'
import { SWRConfig } from 'swr'

const sourceCode = Source_Code_Pro({
  subsets: ['latin'],
  variable: '--font-source-code',
  display: 'swap',
})

const lato = Lato({
  weight: ['100', '300', '400', '700', '900'],
  subsets: ['latin'],
  variable: '--font-lato',
  display: 'swap',
})

const SWRConfigWithAuth: FC<{ children: ReactNode }> = ({ children }) => {
  const { apiFetcher } = useApiFetcher()
  return (
    <SWRConfig
      value={{
        fetcher: apiFetcher,
      }}
    >
      {children}
    </SWRConfig>
  )
}

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <SubscriptionProvider>
        <WithSubscription>
          <AppContextProvider>
            <WithAnalytics>
              <SWRConfigWithAuth>
                <div
                  className={cn(
                    lato.variable,
                    sourceCode.variable,
                    'font-lato',
                  )}
                >
                  <Component {...pageProps} />
                </div>
              </SWRConfigWithAuth>
            </WithAnalytics>
          </AppContextProvider>
        </WithSubscription>
      </SubscriptionProvider>
    </AuthProvider>
  )
}
