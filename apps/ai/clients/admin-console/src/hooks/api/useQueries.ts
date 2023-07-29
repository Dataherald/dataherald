import MOCK_QUERIES from '@/mocks/queries'
import { Queries } from '@/models/api'
import useSWRInfinite from 'swr/infinite'

const PAGE_SIZE = 10

const fetcher = (url: string): Promise<Queries> => {
  return new Promise((resolve) => {
    const params = new URLSearchParams(url.split('?')[1])
    const page = Number(params.get('page') || 0)
    const startIdx = page * PAGE_SIZE
    const endIdx = startIdx + PAGE_SIZE

    const timeoutId = setTimeout(() => {
      resolve(MOCK_QUERIES.slice(startIdx, endIdx))
    }, 1000)

    return () => clearTimeout(timeoutId)
  })
}

interface QueriesResponse {
  queries: Queries | undefined
  isLoadingFirst: boolean
  isLoadingMore: boolean
  isReachingEnd: boolean
  page: number
  setPage: (
    page: number | ((_page: number) => number),
  ) => Promise<Queries[] | undefined>
}

const useQueries = (): QueriesResponse => {
  const {
    data: queriesPages,
    size: page,
    setSize: setPage,
    isLoading,
  } = useSWRInfinite<Queries>(
    (index) => `/api/queries?page=${index + 1}`,
    fetcher,
  )

  const queries = queriesPages?.flat()
  const isLoadingFirst = !queries
  const isLoadingMore =
    isLoading ||
    (page > 0 &&
      !!queriesPages &&
      typeof queriesPages[page - 1] === 'undefined')
  const isEmpty = queriesPages?.[0]?.length === 0
  const isReachingEnd =
    isEmpty ||
    (!!queriesPages &&
      queriesPages[queriesPages.length - 1]?.length < PAGE_SIZE)

  return {
    queries,
    isLoadingFirst,
    isLoadingMore,
    isReachingEnd,
    page,
    setPage,
  }
}

export default useQueries
