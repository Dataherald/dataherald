import WithAnalytics from '@/components/hoc/WithAnalytics'
import WithSubscription from '@/components/hoc/WithSubscription'
import { AppContextProvider } from '@/contexts/app-context'
import { AuthProvider } from '@/contexts/auth-context'
import { SubscriptionProvider } from '@/contexts/subscription-context'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { cn } from '@/lib/utils'
import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { Nunito_Sans, Source_Code_Pro } from 'next/font/google'
import { FC, ReactNode } from 'react'
import { SWRConfig } from 'swr'

export const sourceCode = Source_Code_Pro({
  subsets: ['latin'],
  variable: '--font-source-code',
  display: 'swap',
})

export const mainFont = Nunito_Sans({
  weight: ['300', '400', '700', '900'],
  subsets: ['latin'],
  variable: '--font-main',
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
                    sourceCode.variable,
                    mainFont.variable,
                    'font-main',
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
