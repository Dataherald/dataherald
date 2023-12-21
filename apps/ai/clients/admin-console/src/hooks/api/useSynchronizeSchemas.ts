import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback } from 'react'

const useSynchronizeSchemas = () => {
  const { apiFetcher } = useApiFetcher()

  const synchronizeSchemas = useCallback(
    async (payload: {
      db_connection_id: string
      table_names: string[]
    }): Promise<void> =>
      apiFetcher<void>(`${API_URL}/table-descriptions/sync-schemas`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    [apiFetcher],
  )
  return synchronizeSchemas
}

export default useSynchronizeSchemas
