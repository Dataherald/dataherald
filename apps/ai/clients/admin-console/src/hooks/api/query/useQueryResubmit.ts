import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { Query } from '@/models/api'
import { useCallback } from 'react'

const useQueryResubmit = () => {
  const apiFetcher = useApiFetcher()

  const resubmitQuery = useCallback(
    async (queryId: string): Promise<Query> =>
      apiFetcher<Query>(`${API_URL}/query/${queryId}/answer`, {
        method: 'POST',
      }),
    [apiFetcher],
  )
  return resubmitQuery
}

export default useQueryResubmit
