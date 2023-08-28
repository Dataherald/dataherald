import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { apiFetcher } from '@/lib/api/fetcher'
import { Databases } from '@/models/api'
import useSWR from 'swr'

interface DatabasesResponse {
  databases: Databases | undefined
  isLoading: boolean
  error: unknown
}

const useDatabases = (): DatabasesResponse => {
  const { token } = useAuth()
  const { data, isLoading, error } = useSWR<Databases>(
    token ? [`${API_URL}/database/list`, token] : null,
    ([url, token]: [string, string]) => apiFetcher<Databases>(url, { token }),
  )
  return {
    databases: data,
    isLoading,
    error,
  }
}

export default useDatabases
