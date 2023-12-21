import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { Query } from '@/models/api'
import useSWR from 'swr'

export const useQuery = (promptId: string) => {
  const { token } = useAuth()

  const { data, isLoading, error, mutate } = useSWR<Query>(
    token && promptId ? `${API_URL}/generations/${promptId}` : null,
  )

  return {
    query: data,
    isLoading,
    error,
    mutate,
  }
}
