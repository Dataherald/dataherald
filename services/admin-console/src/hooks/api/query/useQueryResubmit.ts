import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { Query } from '@/models/api'
import { useCallback } from 'react'

const useQueryResubmit = () => {
  const { apiFetcher } = useApiFetcher()

  const resubmitQuery = useCallback(
    async (promptId: string): Promise<Query> =>
      apiFetcher<Query>(`${API_URL}/generations/${promptId}`, {
        method: 'POST',
      }),
    [apiFetcher],
  )
  return resubmitQuery
}

export default useQueryResubmit
