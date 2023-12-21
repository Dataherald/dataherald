import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { Query, QueryStatus } from '@/models/api'
import { useCallback } from 'react'

export interface QueryPutRequest {
  generation_status?: QueryStatus
  message?: string
}

const useQueryPut = () => {
  const { apiFetcher } = useApiFetcher()

  const patchQuery = useCallback(
    async (promptId: string, puts: QueryPutRequest): Promise<Query> =>
      apiFetcher<Query>(`${API_URL}/generations/${promptId}`, {
        method: 'PUT',
        body: JSON.stringify(puts),
      }),
    [apiFetcher],
  )
  return patchQuery
}

export default useQueryPut
