import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { apiFetcher } from '@/lib/api/fetcher'
import { DatabaseConnection } from '@/models/api'
import { useCallback } from 'react'

const usePostDatabaseConnection = () => {
  const { token } = useAuth()

  const connectDatabase = useCallback(
    async (dbConnection: DatabaseConnection, file?: File) => {
      const formData = new FormData()

      if (file) {
        formData.append('file', file, file.name)
      }

      formData.append(
        'db_connection_request_json',
        JSON.stringify(JSON.stringify(dbConnection)),
      )

      return apiFetcher<DatabaseConnection>(`${API_URL}/database-connection`, {
        method: 'POST',
        body: formData,
        token: token as string,
      })
    },
    [token],
  )

  return connectDatabase
}

export default usePostDatabaseConnection
