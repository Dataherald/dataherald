import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback } from 'react'

const useGet = <Model>() => {
  const apiFetcher = useApiFetcher()

  const get = useCallback(
    async (url: string) => {
      try {
        return await apiFetcher<Model>(url, {
          method: 'GET',
        })
      } catch (error) {
        console.error('Get operation failed:', error)
        throw error
      }
    },
    [apiFetcher],
  )

  return get
}

export default useGet
