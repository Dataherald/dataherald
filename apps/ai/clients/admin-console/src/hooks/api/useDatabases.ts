import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { Databases } from '@/models/api'
import { useEffect, useState } from 'react'
import useSWR from 'swr'

interface DatabasesResponse {
  databases: Databases | undefined
  isLoading: boolean
  error: unknown
  mutate: (optimisticData?: Databases) => Promise<Databases | void>
  updateDatabases: (data: Databases) => void
}

const useDatabases = (): DatabasesResponse => {
  const endpointUrl = `${API_URL}/table-descriptions/database/list`
  const { token } = useAuth()
  const { apiFetcher } = useApiFetcher()
  const {
    data: serverData,
    isLoading,
    error,
    mutate: swrMutate,
  } = useSWR<Databases>(token ? endpointUrl : null, {
    revalidateIfStale: false,
    revalidateOnFocus: false,
  })

  const [data, setData] = useState<Databases | undefined>(serverData)

  const optimisticMutate = async (optimisticDatabases?: Databases) =>
    new Promise<Databases | void>((resolve, reject) => {
      return swrMutate(apiFetcher<Databases>(endpointUrl), {
        optimisticData: optimisticDatabases || serverData,
        revalidate: false,
        rollbackOnError: true,
      })
        .then(resolve)
        .catch(reject)
    })

  const updateDatabases = (databases: Databases) => {
    setData(databases)
  }

  useEffect(() => setData(serverData), [serverData])

  return {
    databases: data,
    isLoading: isLoading || (!data && !error),
    error,
    mutate: optimisticMutate,
    updateDatabases,
  }
}

export default useDatabases
