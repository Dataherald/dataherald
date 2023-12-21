import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { Databases } from '@/models/api'
import { useState } from 'react'
import useSWR from 'swr'

interface DatabasesResponse {
  databases: Databases | undefined
  isLoading: boolean
  error: unknown
  mutate: (optimisticData?: Databases) => Promise<Databases | void>
}

const useDatabases = (): DatabasesResponse => {
  const endpointUrl = `${API_URL}/table-descriptions/database/list`
  const { token } = useAuth()
  const { apiFetcher } = useApiFetcher()
  const {
    data,
    isLoading,
    error,
    mutate: swrMutate,
  } = useSWR<Databases>(token ? endpointUrl : null, {
    revalidateIfStale: false,
    revalidateOnFocus: false,
  })

  const [isValidating, setIsValidating] = useState(false)

  const optimisticMutate = async (optimisticDatabases?: Databases) =>
    new Promise<Databases | void>((resolve, reject) => {
      setIsValidating(true)
      return swrMutate(apiFetcher<Databases>(endpointUrl), {
        optimisticData: optimisticDatabases || data,
        revalidate: false,
        rollbackOnError: true,
      })
        .then(resolve)
        .catch(reject)
        .finally(() => setIsValidating(false))
    })

  return {
    databases: data,
    isLoading: isLoading || isValidating || (!data && !error),
    error,
    mutate: optimisticMutate,
  }
}

export default useDatabases
