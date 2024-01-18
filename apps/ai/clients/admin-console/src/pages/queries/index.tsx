import { DataTable } from '@/components/data-table/data-table'
import { LoadingTable } from '@/components/data-table/loading-table'
import PageLayout from '@/components/layout/page-layout'
import { columns as cols } from '@/components/queries/columns'
import QueriesError from '@/components/queries/error'
import { Button } from '@/components/ui/button'
import { ContentBox } from '@/components/ui/content-box'
import useQueries from '@/hooks/api/query/useQueries'
import { QueryListItem } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { RefreshCcw } from 'lucide-react'
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

  if (!isLoadingFirst && error) {
    pageContent = <QueriesError />
  } else if (isLoadingFirst) {
    pageContent = <LoadingTable />
  } else
    pageContent = (
      <DataTable
        columns={columns}
        data={items}
        enableFiltering
        isLoadingMore={isLoadingMore}
        isReachingEnd={isReachingEnd}
        isRefreshing={isRefreshing}
        onRowClick={handleQueryClick}
        onLoadMore={handleLoadMore}
        onRefresh={handleRefresh}
        noMoreDataMessage="No more queries"
      />
    )

  return (
    <PageLayout>
      <ContentBox className="m-6">{pageContent}</ContentBox>
    </PageLayout>
  )
}

export default withPageAuthRequired(QueriesPage)
