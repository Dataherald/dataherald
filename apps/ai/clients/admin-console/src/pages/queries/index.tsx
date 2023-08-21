import PageLayout from '@/components/layout/page-layout'
import { columns as cols } from '@/components/queries/columns'
import { DataTable } from '@/components/queries/data-table'
import QueriesError from '@/components/queries/error'
import { LoadingTable } from '@/components/queries/loading-table'
import { Button } from '@/components/ui/button'
import useQueries from '@/hooks/api/useQueries'
import { cn } from '@/lib/utils'
import { QueryListItem } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { RefreshCw } from 'lucide-react'
import { useRouter } from 'next/router'
import { FC, useMemo, useState } from 'react'

const QueriesPage: FC = () => {
  const {
    queries = [],
    isLoadingFirst,
    isLoadingMore,
    isReachingEnd,
    error,
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

  let pageContent: JSX.Element = <></>

  if (error) {
    pageContent = <QueriesError />
  } else if (isLoadingFirst) {
    pageContent = (
      <div className="rounded-xl border bg-gray-50 p-6">
        <LoadingTable />
      </div>
    )
  } else
    pageContent = (
      <div className="grow overflow-auto flex flex-col gap-4 rounded-xl border bg-gray-50 p-6">
        <div className="flex items-center justify-between bg-gray-50 py-0">
          <h1 className="font-bold">Latest Queries</h1>
          <Button
            variant="outline"
            className="bg-gray-50"
            onClick={handleRefresh}
          >
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

  return <PageLayout>{pageContent}</PageLayout>
}

export default withPageAuthRequired(QueriesPage)
