import MOCK_QUERIES from '@/mocks/queries'
import { Query } from '@/models/api'
import useSWR from 'swr'

const fetcher = (url: string) => {
  const queryId = url.split('/').pop() || ''
  return new Promise<Query>((resolve) => {
    const timer = setTimeout(() => {
      resolve(MOCK_QUERIES.find((query) => query.id === queryId) as Query)
    }, 1000)

    return () => clearTimeout(timer)
  })
}

export const useQuery = (queryId: string) => {
  const { data, isLoading, error } = useSWR<Query>(
    `/api/query/${queryId}`,
    fetcher,
  )

  return {
    query: data,
    isLoading,
    error,
  }
}
