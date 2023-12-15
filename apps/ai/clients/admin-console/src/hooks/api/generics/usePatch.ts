import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback } from 'react'

const usePatch = <T>() => {
  const { apiFetcher } = useApiFetcher()

  const patch = useCallback(
    async (url: string, updates: Partial<T>) => {
      try {
        return await apiFetcher<T>(url, {
          method: 'PATCH',
          body: JSON.stringify(updates),
        })
      } catch (error) {
        console.error('PATCH operation failed:', error)
        throw error
      }
    },
    [apiFetcher],
  )

  return patch
}

export default usePatch
