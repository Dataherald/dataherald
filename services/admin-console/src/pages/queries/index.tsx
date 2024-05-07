import { DataTable } from '@/components/data-table'
import PageErrorMessage from '@/components/error/page-error-message'
import PageLayout from '@/components/layout/page-layout'
import { getColumns } from '@/components/queries/columns'
import { ContentBox } from '@/components/ui/content-box'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { useAppContext } from '@/contexts/app-context'
import useQueries from '@/hooks/api/query/useQueries'
import { QueryListItem } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { Info } from 'lucide-react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { FC, useMemo, useState } from 'react'

const QueriesPage: FC = () => {
  const { organization } = useAppContext()
  const {
    items = [],
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
  } = useQueries()
  const columns = useMemo(
    () =>
      getColumns({
        hiddenColumns: { slack_message_sent: !organization?.slack_config },
      }),
    [organization?.slack_config],
  )
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

  const searchInfo = (
    <TooltipProvider>
      <Tooltip delayDuration={0}>
        <TooltipTrigger asChild>
          <Info size={18} className="text-slate-600" />
        </TooltipTrigger>
        <TooltipContent>
          Search queries by <strong>question</strong> or{' '}
          <strong>generated SQL</strong> fields.
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )

  if (error) {
    pageContent = (
      <PageErrorMessage
        message="Something went wrong while fetching your organization queries."
        error={error}
      />
    )
  } else
    pageContent = (
      <DataTable
        id="queries"
        columns={columns}
        data={items}
        enableColumnVisibility
        isLoadingFirst={isLoadingFirst}
        isLoadingMore={isLoadingMore}
        isReachingEnd={isReachingEnd}
        isRefreshing={isRefreshing}
        searchText={searchText}
        searchInfo={searchInfo}
        onSearchTextChange={setSearchText}
        onSearchTextClear={clearSearchText}
        onRowClick={handleQueryClick}
        onLoadMore={handleLoadMore}
        onRefresh={handleRefresh}
        noMoreDataMessage="No more queries"
      />
    )

  return (
    <PageLayout>
      <Head>
        <title>Queries - Dataherald API</title>
      </Head>
      <ContentBox className="m-6">{pageContent}</ContentBox>
    </PageLayout>
  )
}

export default withPageAuthRequired(QueriesPage)
