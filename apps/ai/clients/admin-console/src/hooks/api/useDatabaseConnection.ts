import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { DatabaseConnection, ErrorResponse } from '@/models/api'
import useSWR from 'swr'

interface DatabaseConnectionResponse {
  databaseConnection: DatabaseConnection | undefined
  isLoading: boolean
  error: ErrorResponse | null
}

const useDatabaseConnection = (
  databaseConnectionId?: string,
): DatabaseConnectionResponse => {
  const endpointUrl = `${API_URL}/database-connections/${databaseConnectionId}`
  const { token } = useAuth()
  const { data, isLoading, error } = useSWR<DatabaseConnection>(
    token ? endpointUrl : null,
  )

  return {
    databaseConnection: data,
    isLoading: isLoading || (!data && !error),
    error,
  }
}

export default useDatabaseConnection
