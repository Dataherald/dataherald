import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { apiFetcher } from '@/lib/api/fetcher'
import { useCallback } from 'react'

const useSynchronizeSchemas = () => {
  const { token } = useAuth()

  const synchronizeSchemas = useCallback(
    async (payload: {
      db_connection_id: string
      table_names: string[]
    }): Promise<void> =>
      apiFetcher<void>(`${API_URL}/table-description/sync-schemas`, {
        method: 'POST',
        body: JSON.stringify(payload),
        token: token as string,
      }),
    [token],
  )
  return synchronizeSchemas
}

export default useSynchronizeSchemas
