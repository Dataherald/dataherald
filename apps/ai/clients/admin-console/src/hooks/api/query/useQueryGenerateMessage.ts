import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback } from 'react'

interface GenerateMessageResponse {
  created_at: string
  id: string
  metadata: Record<string, unknown>
  sql_generation_id: string
  text: string
}

const useQueryGenerateMessage = () => {
  const { apiFetcher } = useApiFetcher()

  const generateMessage = useCallback(
    async (promptId: string): Promise<GenerateMessageResponse> =>
      apiFetcher<GenerateMessageResponse>(
        `${API_URL}/generations/${promptId}/nl-generations`,
        {
          method: 'POST',
          body: JSON.stringify({}),
        },
      ),
    [apiFetcher],
  )
  return generateMessage
}

export default useQueryGenerateMessage
