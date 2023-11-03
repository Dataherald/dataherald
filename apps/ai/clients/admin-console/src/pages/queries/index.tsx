import { DataTable } from '@/components/data-table/data-table'
import { LoadingTable } from '@/components/data-table/loading-table'
import PageLayout from '@/components/layout/page-layout'
import { columns as cols } from '@/components/queries/columns'
import QueriesError from '@/components/queries/error'
import { Button } from '@/components/ui/button'
import { ContentBox } from '@/components/ui/content-box'
import useQueries from '@/hooks/api/query/useQueries'
import { buildIdHref, cn } from '@/lib/utils'
import { QueryListItem } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { RefreshCw } from 'lucide-react'
import { useRouter } from 'next/router'
import { FC, useMemo, useState } from 'react'

const QueriesPage: FC = () => {
  const {
    items = [],
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
    router.push(buildIdHref('/queries', query.id, query.display_id))

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

  if (!isLoadingFirst && error) {
    pageContent = <QueriesError />
  } else if (isLoadingFirst) {
    pageContent = <LoadingTable />
  } else
    pageContent = (
      <DataTable
        columns={columns}
        data={items}
        isLoadingMore={isLoadingMore}
        isReachingEnd={isReachingEnd}
        onRowClick={handleQueryClick}
        onLoadMore={handleLoadMore}
      />
    )

  return (
    <PageLayout>
      <ContentBox className="overflow-auto m-6">
        <div className="flex items-center justify-between bg-gray-50 py-0">
          <h1 className="font-bold">Latest Queries</h1>
          <Button
            variant="outline"
            className="bg-gray-50"
            disabled={isLoadingFirst}
            onClick={handleRefresh}
          >
            <RefreshCw
              size={18}
              className={cn('mr-2', isRefreshing ? 'animate-spin' : '')}
            />{' '}
            {!isRefreshing ? 'Refresh' : 'Refreshing'}
          </Button>
        </div>
        {pageContent}
      </ContentBox>
    </PageLayout>
  )
}

export default withPageAuthRequired(QueriesPage)
