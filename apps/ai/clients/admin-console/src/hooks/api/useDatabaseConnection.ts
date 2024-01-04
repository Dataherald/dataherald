import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { DatabaseConnection } from '@/models/api'
import useSWR from 'swr'

interface DatabaseConnectionResponse {
  databaseConnection: DatabaseConnection | undefined
  isLoading: boolean
  error: unknown
}

const useDatabaseConnection = (
  databaseConnectionId?: string,
): DatabaseConnectionResponse => {
  const endpointUrl = `${API_URL}/database-connections/${databaseConnectionId}`
  const { token } = useAuth()
  const { data, isLoading, error } = useSWR<DatabaseConnection>(
    token && databaseConnectionId ? endpointUrl : null,
  )

  return {
    databaseConnection: data,
    isLoading: isLoading || (!data && !error),
    error,
  }
}

export default useDatabaseConnection
