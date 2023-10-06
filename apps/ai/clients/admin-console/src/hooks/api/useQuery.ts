import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { Query } from '@/models/api'
import useSWR from 'swr'

export const useQuery = (queryId: string) => {
  const { token } = useAuth()

  const { data, isLoading, error, mutate } = useSWR<Query>(
    token && queryId ? `${API_URL}/query/${queryId}` : null,
  )

  return {
    query: data,
    isLoading,
    error,
    mutate,
  }
}
