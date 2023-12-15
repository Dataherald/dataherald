import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback } from 'react'

const useQuerySendMessage = () => {
  const { apiFetcher } = useApiFetcher()

  const sendMessage = useCallback(
    async (queryId: string): Promise<void> =>
      apiFetcher<void>(`${API_URL}/query/${queryId}/message`, {
        method: 'POST',
      }),
    [apiFetcher],
  )
  return sendMessage
}

export default useQuerySendMessage
