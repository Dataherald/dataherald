import { apiFetcher } from '@/lib/api/fetcher'
import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { SWRConfig } from 'swr'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <SWRConfig
      value={{
        fetcher: apiFetcher,
      }}
    >
      <Component {...pageProps} />
    </SWRConfig>
  )
}
