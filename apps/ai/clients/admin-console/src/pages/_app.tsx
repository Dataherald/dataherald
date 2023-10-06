import { AuthProvider } from '@/contexts/auth-context'
import useApiFetcher from '@/hooks/api/useApiFetcher'
import { cn } from '@/lib/utils'
import '@/styles/globals.css'
import { UserProvider } from '@auth0/nextjs-auth0/client'
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
  const apiFetcher = useApiFetcher()
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
    <UserProvider>
      <AuthProvider>
        <SWRConfigWithAuth>
          <div className={cn(lato.variable, sourceCode.variable, 'font-lato')}>
            <Component {...pageProps} />
          </div>
        </SWRConfigWithAuth>
      </AuthProvider>
    </UserProvider>
  )
}
