import {
  DEFAULT_PAGE_SIZE,
  List,
  PageResponse,
} from '@/hooks/api/generics/usePagination'
import { useCallback, useState } from 'react'
import useSWRInfinite from 'swr/infinite'

const useMockPagination = <T>(
  mockData: List<T>,
  pageSize = DEFAULT_PAGE_SIZE,
  delayDuration = 1000,
): PageResponse<T> => {
  const fetchMockData = (page: number) => {
    return new Promise<List<T>>((resolve) => {
      setTimeout(() => {
        const start = page * pageSize
        const end = start + pageSize
        resolve(mockData.slice(start, end) as List<T>)
      }, delayDuration)
    })
  }

  const {
    data: pages,
    size: page,
    setSize: setPage,
    isLoading,
    error,
    mutate,
  } = useSWRInfinite<List<T>>(
    (index) => `${index}`,
    (page) => fetchMockData(parseInt(page as string)),
  )

  const [searchText, setSearchText] = useState('')
  const clearSearchText = useCallback(() => setSearchText(''), [])
  const items = pages?.flat()
  const isLoadingFirst = !items
  const isLoadingMore =
    isLoading || (page > 0 && !!pages && typeof pages[page - 1] === 'undefined')
  const isEmpty = pages?.[0]?.length === 0
  const isReachingEnd =
    isEmpty || (!!pages && pages[pages.length - 1]?.length < pageSize)

  return {
    items,
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

export default useMockPagination
