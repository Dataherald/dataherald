import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { Query } from '@/models/api'
import { useCallback } from 'react'

const useQuerySubmit = () => {
  const { apiFetcher, cancelApiFetch } = useApiFetcher()

  const submitQuery = useCallback(
    async (prompt: string): Promise<Query> =>
      apiFetcher<Query>(`${API_URL}/generations/sql-generations/execute`, {
        method: 'POST',
        body: JSON.stringify({ prompt }),
      }),
    [apiFetcher],
  )
  return { submitQuery, cancelSubmitQuery: cancelApiFetch }
}

export default useQuerySubmit
