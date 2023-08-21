import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { apiFetcher } from '@/lib/api/fetcher'
import { Query } from '@/models/api'
import useSWR from 'swr'

export const useQuery = (queryId: string) => {
  const { token } = useAuth()
  const { data, isLoading, error, mutate } = useSWR<Query>(
    token && queryId ? [`${API_URL}/query/${queryId}`, token] : null,
    ([url, token]: [string, string]) => apiFetcher<Query>(url, { token }),
  )

  return {
    query: data,
    isLoading,
    error,
    mutate,
  }
}
