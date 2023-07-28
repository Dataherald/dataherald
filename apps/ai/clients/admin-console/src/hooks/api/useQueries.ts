import MOCK_QUERIES from '@/mocks/queries'
import { Queries } from '@/models/api'
import { useEffect, useState } from 'react'

interface QueriesResponse {
  queries?: Queries
  loading: boolean
  error: unknown
}

const useQueries = (): QueriesResponse => {
  const [data, setData] = useState<Queries | undefined>(undefined)
  const [loading, setLoading] = useState(true)
  const error = undefined

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setData(MOCK_QUERIES)
      setLoading(false)
    }, 2000)

    return () => clearTimeout(timeoutId)
  }, [])

  return {
    queries: data,
    loading,
    error,
  }
}

export default useQueries
