import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { apiFetcher } from '@/lib/api/fetcher'
import { QueryList } from '@/models/api'
import { KeyedMutator } from 'swr'
import useSWRInfinite from 'swr/infinite'

const PAGE_SIZE = 10

interface QueriesResponse {
  queries: QueryList | undefined
  isLoadingFirst: boolean
  isLoadingMore: boolean
  isReachingEnd: boolean
  error: unknown
  page: number
  setPage: (
    page: number | ((_page: number) => number),
  ) => Promise<QueryList[] | undefined>
  mutate: KeyedMutator<QueryList[]>
}

const useQueries = (): QueriesResponse => {
  const { token } = useAuth()

  const {
    data: queriesPages,
    size: page,
    setSize: setPage,
    isLoading,
    error,
    mutate,
  } = useSWRInfinite<QueryList>(
    (index) =>
      token
        ? [`${API_URL}/query/list?page=${index}&page_size=${PAGE_SIZE}`, token]
        : null,
    ([url, token]: [string, string]) => apiFetcher<QueryList>(url, { token }),
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
    error,
    page,
    setPage,
    mutate,
  }
}

export default useQueries
