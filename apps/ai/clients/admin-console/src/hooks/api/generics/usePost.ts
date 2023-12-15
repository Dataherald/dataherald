import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback } from 'react'

const usePost = <T>() => {
  const { apiFetcher } = useApiFetcher()

  const post = useCallback(
    async (url: string, resource: T) => {
      try {
        return await apiFetcher<T>(url, {
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
