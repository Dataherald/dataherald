import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback } from 'react'

const usePost = <Request, Response = Request>() => {
  const { apiFetcher } = useApiFetcher()

  const post = useCallback(
    async (url: string, resource: Request) => {
      try {
        return await apiFetcher<Response>(url, {
          method: 'POST',
          body: JSON.stringify(resource),
        })
      } catch (error) {
        console.error('POST operation failed:', error)
        throw error
      }
    },
    [apiFetcher],
  )

  return post
}

export default usePost
