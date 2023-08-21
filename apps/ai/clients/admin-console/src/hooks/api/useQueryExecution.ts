import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { apiFetcher } from '@/lib/api/fetcher'
import { Query } from '@/models/api'
import { useCallback } from 'react'

const useQueryExecution = () => {
  const { token } = useAuth()

  const executeQuery = useCallback(
    async (queryId: string, sql_query: string): Promise<Query> =>
      apiFetcher<Query>(`${API_URL}/query/${queryId}/execution`, {
        method: 'POST',
        body: JSON.stringify({ sql_query }),
        token: token as string,
      }),
    [token],
  )
  return executeQuery
}

export default useQueryExecution
