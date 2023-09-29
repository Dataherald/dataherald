import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { apiFetcher } from '@/lib/api/fetcher'
import { Databases } from '@/models/api'
import useSWR from 'swr'

interface DatabasesResponse {
  databases: Databases | undefined
  isLoading: boolean
  error: unknown
  mutate: (optimisticData?: Databases) => Promise<Databases | void>
}

const useDatabases = (): DatabasesResponse => {
  const endpointUrl = `${API_URL}/table-description/database/list`
  const { token } = useAuth()
  const swrKey = token ? [endpointUrl, token] : null
  const {
    data,
    isLoading,
    isValidating,
    error,
    mutate: swrMutate,
  } = useSWR<Databases>(
    swrKey,
    ([url, token]: [string, string]) => apiFetcher<Databases>(url, { token }),
    { revalidateIfStale: false, revalidateOnFocus: false },
  )

  const optimisticMutate = async (optimisticDatabases?: Databases) =>
    swrMutate(apiFetcher<Databases>(endpointUrl, { token: token as string }), {
      optimisticData: optimisticDatabases || data,
      revalidate: false,
      rollbackOnError: true,
    })

  return {
    databases: data,
    isLoading: isLoading || isValidating || (!data && !error),
    error,
    mutate: optimisticMutate,
  }
}

export default useDatabases
