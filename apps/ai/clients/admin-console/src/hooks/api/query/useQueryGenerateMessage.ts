import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback } from 'react'

interface GenerateMessageResponse {
  message: string
}

const useQueryGenerateMessage = () => {
  const apiFetcher = useApiFetcher()

  const generateMessage = useCallback(
    async (queryId: string): Promise<GenerateMessageResponse> =>
      apiFetcher<GenerateMessageResponse>(
        `${API_URL}/query/${queryId}/message`,
        {
          method: 'PATCH',
          body: JSON.stringify({}),
        },
      ),
    [apiFetcher],
  )
  return generateMessage
}

export default useQueryGenerateMessage
