import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback } from 'react'

const usePut = <T>() => {
  const { apiFetcher } = useApiFetcher()

  const put = useCallback(
    async (url: string, resource: T) => {
      try {
        return await apiFetcher<T>(url, {
          method: 'PUT',
          body: JSON.stringify(resource),
        })
      } catch (error) {
        console.error('PUT operation failed \n', error)
        throw error
      }
    },
    [apiFetcher],
  )

  return put
}

export default usePut
