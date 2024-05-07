import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback } from 'react'

const useGet = <T>() => {
  const { apiFetcher } = useApiFetcher()

  const get = useCallback(
    async (url: string) => {
      try {
        return await apiFetcher<T>(url, {
          method: 'GET',
        })
      } catch (error) {
        console.error('GET operation failed:', error)
        throw error
      }
    },
    [apiFetcher],
  )

  return get
}

export default useGet
