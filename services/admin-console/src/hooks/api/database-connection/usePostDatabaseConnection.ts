import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { DatabaseConnection } from '@/models/api'
import { useCallback } from 'react'

const usePostDatabaseConnection = () => {
  const { apiFetcher } = useApiFetcher()

  const connectDatabase = useCallback(
    async (dbConnection: DatabaseConnection, file?: File | null) => {
      const formData = new FormData()

      if (file) {
        formData.append('file', file, file.name)
      }

      formData.append('request_json', JSON.stringify(dbConnection))

      return apiFetcher<DatabaseConnection>(`${API_URL}/database-connections`, {
        method: 'POST',
        body: formData,
      })
    },
    [apiFetcher],
  )

  return connectDatabase
}

export default usePostDatabaseConnection
