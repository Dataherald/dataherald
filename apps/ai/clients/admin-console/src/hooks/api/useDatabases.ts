import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { apiFetcher } from '@/lib/api/fetcher'
import { Databases } from '@/models/api'
import useSWR, { KeyedMutator } from 'swr'

interface DatabasesResponse {
  databases: Databases | undefined
  isLoading: boolean
  error: unknown
  mutate: KeyedMutator<Databases>
}

const useDatabases = (): DatabasesResponse => {
  const { token } = useAuth()
  const { data, isLoading, isValidating, error, mutate } = useSWR<Databases>(
    token ? [`${API_URL}/table-description/database/list`, token] : null,
    ([url, token]: [string, string]) => apiFetcher<Databases>(url, { token }),
    { revalidateIfStale: false, revalidateOnFocus: false },
  )
  return {
    databases: data,
    isLoading: isLoading || isValidating || (!data && !error),
    error,
    mutate,
  }
}

export default useDatabases
