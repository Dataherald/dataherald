import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { apiFetcher } from '@/lib/api/fetcher'
import { Query, QueryStatus } from '@/models/api'
import { useCallback } from 'react'

const usePatchQuery = () => {
  const { token } = useAuth()

  const patchQuery = useCallback(
    async (
      queryId: string,
      patches: {
        sql_query: string
        query_status: QueryStatus
      },
    ): Promise<Query> =>
      apiFetcher<Query>(`${API_URL}/query/${queryId}`, {
        method: 'PATCH',
        body: JSON.stringify(patches),
        token: token as string,
      }),
    [token],
  )
  return patchQuery
}

export default usePatchQuery
