import { columns as cols } from '@/components/queries/columns'
import { DataTable } from '@/components/queries/data-table'
import { LoadingTable } from '@/components/queries/loading-table'
import { Button } from '@/components/ui/button'
import useQueries from '@/hooks/api/useQueries'
import { cn } from '@/lib/utils'
import { QueryListItem } from '@/models/api'
import { RefreshCw } from 'lucide-react'
import { useRouter } from 'next/router'
import { useMemo, useState } from 'react'

export default function QueriesPage() {
  const {
    queries = [],
    isLoadingFirst,
    isLoadingMore,
    isReachingEnd,
    page,
    setPage,
    mutate,
  } = useQueries()
  const columns = useMemo(() => cols, [])
  const router = useRouter()
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleQueryClick = (query: QueryListItem) =>
    router.push(`/queries/${query.id}`)

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await mutate()
    setIsRefreshing(false)
  }

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
      <div className="flex items-center justify-between bg-gray-50 py-0">
        <h1 className="font-bold">Latest Queries</h1>
        <Button variant="outline" onClick={handleRefresh}>
          <RefreshCw
            size={18}
            className={cn('mr-2', isRefreshing ? 'animate-spin' : '')}
          />{' '}
          {!isRefreshing ? 'Refresh' : 'Refreshing'}
        </Button>
      </div>
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
