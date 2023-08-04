import { API_URL } from '@/config'
import { Query } from '@/models/api'
import useSWR from 'swr'

export const useQuery = (queryId: string) => {
  const { data, isLoading, error } = useSWR<Query>(
    `${API_URL}/query/${queryId}`,
  )

  return {
    query: data,
    isLoading,
    error,
  }
}
