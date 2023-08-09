import PageLayout from '@/components/layout/page-layout'
import { apiFetcher } from '@/lib/api/fetcher'
import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { Lato, Source_Code_Pro } from 'next/font/google'
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

export default function App({ Component, pageProps }: AppProps) {
  return (
    <SWRConfig
      value={{
        fetcher: apiFetcher,
      }}
    >
      <PageLayout
        className={`${lato.variable} ${sourceCode.variable} font-lato`}
      >
        <Component {...pageProps} />
      </PageLayout>
    </SWRConfig>
  )
}
