import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { ErrorResponse, SampleDatabaseConnections } from '@/models/api'
import useSWR from 'swr'

interface SampleDatabaseConnectionResponse {
  sampleDBConnections: SampleDatabaseConnections | undefined
  isLoading: boolean
  error: ErrorResponse | null
}

const useSampleDatabaseConnections = (): SampleDatabaseConnectionResponse => {
  const endpointUrl = `${API_URL}/database-connections/sample`
  const { token } = useAuth()
  const { data, isLoading, error } = useSWR<SampleDatabaseConnections>(
    token ? endpointUrl : null,
  )

  return {
    sampleDBConnections: data,
    isLoading: isLoading || (!data && !error),
    error,
  }
}

export default useSampleDatabaseConnections
