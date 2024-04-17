import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { DatabaseConnections, ErrorResponse } from '@/models/api'
import useSWR from 'swr'

interface DatabaseConnectionResponse {
  dbConnections: DatabaseConnections | undefined
  isLoading: boolean
  error: ErrorResponse | null
}

const useDatabaseConnections = (): DatabaseConnectionResponse => {
  const endpointUrl = `${API_URL}/database-connections`
  const { token } = useAuth()
  const { data, isLoading, error } = useSWR<DatabaseConnections>(
    token ? endpointUrl : null,
  )

  return {
    dbConnections: data,
    isLoading: isLoading || (!data && !error),
    error,
  }
}

export default useDatabaseConnections
