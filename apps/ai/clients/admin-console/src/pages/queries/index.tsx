import { columns as cols } from '@/components/queries/columns'
import { DataTable } from '@/components/queries/data-table'
import { LoadingTable } from '@/components/queries/loading-table'
import useQueries from '@/hooks/api/useQueries'
import { QueryListItem } from '@/models/api'
import { useRouter } from 'next/navigation'
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
  const router = useRouter()

  const handleQueryClick = (query: QueryListItem) =>
    router.push(`/queries/${query.id}`)

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
      <div className="rounded-xl border bg-gray-50 p-6">
        <LoadingTable />
      </div>
    )
  }

  return (
    <div className="grow overflow-auto flex flex-col gap-4 rounded-xl border bg-gray-50 p-6">
      <h1 className="font-bold">Latest Queries</h1>
      <DataTable
        columns={columns}
        data={queries}
        isLoadingMore={isLoadingMore}
        loadingRef={loadingRef}
        onRowClick={handleQueryClick}
      />
    </div>
  )
}
