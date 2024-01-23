import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { Query } from '@/models/api'
import { useCallback } from 'react'

const useQuerySubmit = () => {
  const { apiFetcher, cancelApiFetch } = useApiFetcher()

  const submitQuery = useCallback(
    async (
      prompt: string,
      db_connection_id: string,
      finetunedModelId?: string,
    ): Promise<Query> =>
      apiFetcher<Query>(`${API_URL}/generations/prompts/sql-generations`, {
        method: 'POST',
        body: JSON.stringify({
          prompt,
          db_connection_id,
          ...(finetunedModelId ? { finetunedModelId } : {}),
        }),
      }),
    [apiFetcher],
  )
  return { submitQuery, cancelSubmitQuery: cancelApiFetch }
}

export default useQuerySubmit
