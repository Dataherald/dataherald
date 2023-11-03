import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { Query, QueryStatus } from '@/models/api'
import { useCallback } from 'react'

export interface QueryPatchRequest {
  query_status?: QueryStatus
  message?: string
}

const useQueryPatch = () => {
  const apiFetcher = useApiFetcher()

  const patchQuery = useCallback(
    async (queryId: string, patches: QueryPatchRequest): Promise<Query> =>
      apiFetcher<Query>(`${API_URL}/query/${queryId}`, {
        method: 'PATCH',
        body: JSON.stringify(patches),
      }),
    [apiFetcher],
  )
  return patchQuery
}

export default useQueryPatch
