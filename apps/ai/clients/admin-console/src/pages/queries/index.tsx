import { DataTable } from '@/components/data-table'
import { LoadingTable } from '@/components/data-table/loading-table'
import PageLayout from '@/components/layout/page-layout'
import { columns as cols } from '@/components/queries/columns'
import QueriesError from '@/components/queries/error'
import { ContentBox } from '@/components/ui/content-box'
import useQueries from '@/hooks/api/query/useQueries'
import { QueryListItem } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import Head from 'next/head'
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
    pageContent = <LoadingTable loadFilters columnLength={7} />
  } else
    pageContent = (
      <DataTable
        columns={columns}
        data={items}
        enableFiltering
        enableColumnVisibility
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
      <Head>
        <title>Queries - Dataherald AI API</title>
      </Head>
      <div className="grow flex flex-col gap-4 m-6">
        <div className="flex flex-col gap-3 max-w-5xl">
          <p>
            Explore the list of queries sourced from our API or Slack
            interactions. Select any query to validate its response in the query
            editor.
          </p>
        </div>
        <ContentBox>{pageContent}</ContentBox>
      </div>
    </PageLayout>
  )
}

export default withPageAuthRequired(QueriesPage)
