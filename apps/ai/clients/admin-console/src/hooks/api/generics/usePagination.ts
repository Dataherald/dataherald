import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { KeyedMutator } from 'swr'
import useSWRInfinite from 'swr/infinite'

export const DEFAULT_PAGE_SIZE = 10

export type List<T> = T[]

export interface PageResponse<T> {
  items: List<T> | undefined
  isLoadingFirst: boolean
  isLoadingMore: boolean
  isReachingEnd: boolean
  error: unknown
  page: number
  setPage: (
    page: number | ((_page: number) => number),
  ) => Promise<List<T>[] | undefined>
  mutate: KeyedMutator<List<T>[]>
}

export type PaginationParams<T> = {
  resourceUrl: string
  pageSize?: number
  itemMapper?: (item: T) => T
}

const usePagination = <T>({
  resourceUrl,
  pageSize = DEFAULT_PAGE_SIZE,
  itemMapper = (item) => item,
}: PaginationParams<T>): PageResponse<T> => {
  const { token } = useAuth()
  const {
    data: pages,
    size: page,
    setSize: setPage,
    isLoading,
    error,
    mutate,
  } = useSWRInfinite<List<T>>(
    (index) =>
      token
        ? `${API_URL}${resourceUrl}?page=${index}&page_size=${pageSize}`
        : null,
    { revalidateAll: true },
  )

  const items = pages?.flat()
  const isLoadingFirst = !items
  const isLoadingMore =
    isLoading || (page > 0 && !!pages && typeof pages[page - 1] === 'undefined')
  const isEmpty = pages?.[0]?.length === 0
  const isReachingEnd =
    isEmpty || (!!pages && pages[pages.length - 1]?.length < pageSize)

  return {
    items: items && items.map(itemMapper),
    isLoadingFirst,
    isLoadingMore,
    isReachingEnd,
    error,
    page,
    setPage,
    mutate,
  }
}

export default usePagination
