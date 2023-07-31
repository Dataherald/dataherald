import PageLayout from '@/components/layout/page-layout'
import { apiFetcher } from '@/lib/api/fetcher'
import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { Lato } from 'next/font/google'
import { SWRConfig } from 'swr'

const lato = Lato({
  weight: ['100', '300', '400', '700', '900'],
  style: ['normal', 'italic'],
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
      <PageLayout className={`${lato.variable} font-lato`}>
        <Component {...pageProps} />
      </PageLayout>
    </SWRConfig>
  )
}
