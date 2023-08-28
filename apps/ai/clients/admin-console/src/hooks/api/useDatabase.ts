import { DATABASE } from '@/mocks/database'
import { Database } from '@/models/api'
import { useMockGetter } from './useMockGetter'

interface DatabaseResponse {
  database: Database | undefined
  isLoading: boolean
  error: unknown
}

const useDatabase = (): DatabaseResponse => {
  const {
    data: database,
    isLoading,
    error,
  } = useMockGetter<Database>('/database', DATABASE, 2000)
  return {
    database,
    isLoading,
    error,
  }
}

export default useDatabase
