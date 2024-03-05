import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import useDebounce from '@/hooks/useDebounce'
import { ErrorResponse } from '@/models/api'
import { useCallback, useEffect, useState } from 'react'
import { KeyedMutator } from 'swr'
import useSWRInfinite from 'swr/infinite'

export const DEFAULT_PAGE_SIZE = 10

export type List<T> = T[]

export interface PageResponse<T> {
  items: List<T> | undefined
  isLoadingFirst: boolean
  isLoadingMore: boolean
  isReachingEnd: boolean
  error: ErrorResponse | null
  page: number
  setPage: (
    page: number | ((_page: number) => number),
  ) => Promise<List<T>[] | undefined>
  searchText: string
  setSearchText: (search: string) => void
  clearSearchText: () => void
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
  const [searchText, setSearchText] = useState('')
  const [searchTextApiParam, setSearchTextApiParam] = useState('')
  const debouncedSearchText = useDebounce(searchText)

  const clearSearchText = useCallback(() => {
    setSearchTextApiParam('')
    setSearchText('')
  }, [])

  useEffect(() => {
    setSearchTextApiParam(debouncedSearchText)
  }, [debouncedSearchText])

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
        ? `${API_URL}${resourceUrl}?page=${index}&page_size=${pageSize}&search_term=${searchTextApiParam}`
        : null,
    { revalidateAll: true },
  )

  const items = pages?.flat()
  const isLoadingFirst = isLoading && !items
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
    searchText,
    setSearchText,
    clearSearchText,
    mutate,
  }
}

export default usePagination
