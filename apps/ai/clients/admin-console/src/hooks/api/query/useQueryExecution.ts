import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { Query } from '@/models/api'
import { useCallback } from 'react'

const useQueryExecution = () => {
  const { apiFetcher } = useApiFetcher()

  const executeQuery = useCallback(
    async (promptId: string, sql: string): Promise<Query> =>
      apiFetcher<Query>(`${API_URL}/generations/${promptId}/sql-generations`, {
        method: 'POST',
        body: JSON.stringify({ sql }),
      }),
    [apiFetcher],
  )
  return executeQuery
}

export default useQueryExecution
