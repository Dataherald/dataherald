import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback } from 'react'

export type ScanRequest = {
  ids: string[]
}

const useSynchronizeSchemas = () => {
  const { apiFetcher } = useApiFetcher()

  const synchronizeSchemas = useCallback(
    async (payload: ScanRequest): Promise<void> =>
      apiFetcher<void>(`${API_URL}/table-descriptions/sync-schemas`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    [apiFetcher],
  )
  return synchronizeSchemas
}

export default useSynchronizeSchemas
