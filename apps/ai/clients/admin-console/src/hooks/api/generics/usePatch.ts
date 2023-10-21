import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback } from 'react'

const usePatch = <PatchModel>() => {
  const apiFetcher = useApiFetcher()

  const patch = useCallback(
    async (url: string, updates: Partial<PatchModel>) => {
      try {
        return await apiFetcher<PatchModel>(url, {
          method: 'PATCH',
          body: JSON.stringify(updates),
        })
      } catch (error) {
        console.error('Patch operation failed:', error)
        throw error
      }
    },
    [apiFetcher],
  )

  return patch
}

export default usePatch
