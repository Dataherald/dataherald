import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { Databases, ErrorResponse } from '@/models/api'
import { useEffect, useState } from 'react'
import useSWR from 'swr'

interface DatabasesResponse {
  databases: Databases | undefined
  isLoading: boolean
  error: ErrorResponse | null
  mutate: (
    optimisticData?: Databases,
    refresh?: boolean,
  ) => Promise<Databases | void>
  updateDatabases: (data: Databases) => void
}

const useDatabases = (): DatabasesResponse => {
  const endpointUrl = `${API_URL}/table-descriptions/database/list`
  const endpointUrlRefresh = `${API_URL}/table-descriptions/refresh-all`
  const { token } = useAuth()
  const { apiFetcher } = useApiFetcher()
  const {
    data: serverData,
    isLoading,
    error,
    mutate: swrMutate,
  } = useSWR<Databases>(token ? endpointUrl : null, {
    refreshInterval: 60000, // 1 minute
  })

  const [data, setData] = useState<Databases | undefined>(serverData)

  const optimisticMutate = async (
    optimisticDatabases?: Databases,
    refresh = false,
  ) =>
    new Promise<Databases | void>((resolve, reject) => {
      let url = endpointUrl
      let options = { method: 'GET' }
      if (refresh) {
        url = endpointUrlRefresh
        options = { method: 'POST' }
      }
      return swrMutate(apiFetcher<Databases>(url, options), {
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
    isLoading,
    error,
    mutate: optimisticMutate,
    updateDatabases,
  }
}

export default useDatabases
