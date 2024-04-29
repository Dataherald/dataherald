import WithAnalytics from '@/components/hoc/WithAnalytics'
import WithApiFetcher from '@/components/hoc/WithApiFetcher'
import WithMobileRedirect from '@/components/hoc/WithMobileRedirect'
import WithSubscription from '@/components/hoc/WithSubscription'
import { AppContextProvider } from '@/contexts/app-context'
import { AuthProvider } from '@/contexts/auth-context'
import { SelfServeProvider } from '@/contexts/self-serve-context'
import { SubscriptionProvider } from '@/contexts/subscription-context'
import { UIProvider } from '@/contexts/ui-context'
import { cn } from '@/lib/utils'
import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { Nunito_Sans, Source_Code_Pro } from 'next/font/google'

export const sourceCode = Source_Code_Pro({
  subsets: ['latin'],
  variable: '--font-source-code',
  display: 'swap',
})

export const mainFont = Nunito_Sans({
  weight: ['300', '400', '500', '600', '700', '800', '900'],
  subsets: ['latin'],
  variable: '--font-main',
  display: 'swap',
})

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <WithMobileRedirect>
        <UIProvider>
          <SubscriptionProvider>
            <WithSubscription>
              <AppContextProvider>
                <WithAnalytics>
                  <WithApiFetcher>
                    <SelfServeProvider>
                      <div
                        className={cn(
                          sourceCode.variable,
                          mainFont.variable,
                          'font-main',
                        )}
                      >
                        <Component {...pageProps} />
                      </div>
                    </SelfServeProvider>
                  </WithApiFetcher>
                </WithAnalytics>
              </AppContextProvider>
            </WithSubscription>
          </SubscriptionProvider>
        </UIProvider>
      </WithMobileRedirect>
    </AuthProvider>
  )
}
