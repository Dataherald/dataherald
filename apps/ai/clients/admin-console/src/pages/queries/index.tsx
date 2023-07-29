import { columns as cols } from '@/components/queries/columns'
import { DataTable } from '@/components/queries/data-table'
import QueriesLayout from '@/components/queries/layout'
import { LoadingTable } from '@/components/queries/loading-table'
import useQueries from '@/hooks/api/useQueries'
import { useEffect, useMemo, useRef } from 'react'

export default function QueriesPage() {
  const {
    queries = [],
    isLoadingFirst,
    isLoadingMore,
    isReachingEnd,
    page,
    setPage,
  } = useQueries()
  const columns = useMemo(() => cols, [])
  const loadingRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isLoadingMore && !isReachingEnd) {
          setPage(page + 1)
        }
      },
      { threshold: 1 },
    )

    const loadingRefCurrent = loadingRef.current

    if (loadingRefCurrent) {
      observer.observe(loadingRefCurrent)
    }

    return () => {
      if (loadingRefCurrent) {
        observer.unobserve(loadingRefCurrent)
      }
    }
  }, [isLoadingMore, isReachingEnd, page, setPage])

  if (isLoadingFirst) {
    return (
      <QueriesLayout>
        <LoadingTable />
      </QueriesLayout>
    )
  }

  return (
    <QueriesLayout>
      <h1 className="font-bold">Latest Queries</h1>
      <DataTable
        columns={columns}
        data={queries}
        isLoadingMore={isLoadingMore}
        loadingRef={loadingRef}
      />
    </QueriesLayout>
  )
}
