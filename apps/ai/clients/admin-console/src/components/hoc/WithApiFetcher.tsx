import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { FC, ReactNode } from 'react'
import { SWRConfig } from 'swr'

const WithApiFetcher: FC<{ children: ReactNode }> = ({ children }) => {
  const { apiFetcher } = useApiFetcher()
  return (
    <SWRConfig
      value={{
        fetcher: apiFetcher,
        errorRetryCount: 0,
      }}
    >
      {children}
    </SWRConfig>
  )
}

export default WithApiFetcher
