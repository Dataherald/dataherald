import { API_URL } from '@/config'
import { Query } from '@/models/api'
import useSWR from 'swr'

export const useQuery = (queryId: string) => {
  const { data, isLoading, error, mutate } = useSWR<Query>(
    queryId ? `${API_URL}/query/${queryId}` : null,
  )

  return {
    query: data,
    isLoading,
    error,
    mutate,
  }
}
