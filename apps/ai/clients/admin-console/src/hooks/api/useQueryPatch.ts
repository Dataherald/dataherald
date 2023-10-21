import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { Query, QueryStatus } from '@/models/api'
import { useCallback } from 'react'

const usePatchQuery = () => {
  const apiFetcher = useApiFetcher()

  const patchQuery = useCallback(
    async (
      queryId: string,
      patches: {
        sql_query: string
        custom_response: string
        query_status: QueryStatus
      },
    ): Promise<Query> =>
      apiFetcher<Query>(`${API_URL}/query/${queryId}`, {
        method: 'PATCH',
        body: JSON.stringify(patches),
      }),
    [apiFetcher],
  )
  return patchQuery
}

export default usePatchQuery
