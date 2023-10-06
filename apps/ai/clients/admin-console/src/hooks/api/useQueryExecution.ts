import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/useApiFetcher'
import { Query } from '@/models/api'
import { useCallback } from 'react'

const useQueryExecution = () => {
  const apiFetcher = useApiFetcher()

  const executeQuery = useCallback(
    async (queryId: string, sql_query: string): Promise<Query> =>
      apiFetcher<Query>(`${API_URL}/query/${queryId}/execution`, {
        method: 'POST',
        body: JSON.stringify({ sql_query }),
      }),
    [apiFetcher],
  )
  return executeQuery
}

export default useQueryExecution
