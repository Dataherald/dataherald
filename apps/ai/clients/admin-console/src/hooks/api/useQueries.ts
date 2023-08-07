import { API_URL } from '@/config'
import { QueryList } from '@/models/api'
import useSWRInfinite from 'swr/infinite'

const PAGE_SIZE = 10

interface QueriesResponse {
  queries: QueryList | undefined
  isLoadingFirst: boolean
  isLoadingMore: boolean
  isReachingEnd: boolean
  page: number
  setPage: (
    page: number | ((_page: number) => number),
  ) => Promise<QueryList[] | undefined>
}

const useQueries = (): QueriesResponse => {
  const {
    data: queriesPages,
    size: page,
    setSize: setPage,
    isLoading,
  } = useSWRInfinite<QueryList>(
    (index) => `${API_URL}/query/list?page=${index}&page_size=${PAGE_SIZE}`,
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
