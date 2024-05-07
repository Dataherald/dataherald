import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback } from 'react'

const useDelete = <T = void>() => {
  const { apiFetcher } = useApiFetcher()

  const deleteResource = useCallback(
    async (url: string) => {
      try {
        return await apiFetcher<T>(url, {
          method: 'DELETE',
        })
      } catch (error) {
        console.error('DELETE operation failed:', error)
        throw error
      }
    },
    [apiFetcher],
  )

  return deleteResource
}

export default useDelete
