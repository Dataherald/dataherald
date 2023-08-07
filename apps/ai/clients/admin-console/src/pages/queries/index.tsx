import { columns as cols } from '@/components/queries/columns'
import { DataTable } from '@/components/queries/data-table'
import { LoadingTable } from '@/components/queries/loading-table'
import useQueries from '@/hooks/api/useQueries'
import { QueryListItem } from '@/models/api'
import { useRouter } from 'next/router'
import { useMemo } from 'react'

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
  const router = useRouter()

  const handleQueryClick = (query: QueryListItem) =>
    router.push(`/queries/${query.id}`)

  const handleLoadMore = () => {
    if (!isLoadingMore) {
      setPage(page + 1)
    }
  }

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
        isReachingEnd={isReachingEnd}
        onRowClick={handleQueryClick}
        onLoadMore={handleLoadMore}
      />
    </div>
  )
}
