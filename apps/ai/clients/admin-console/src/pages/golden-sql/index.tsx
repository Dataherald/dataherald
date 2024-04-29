import { DataTable } from '@/components/data-table'
import PageErrorMessage from '@/components/error/page-error-message'
import { getColumns } from '@/components/golden-sql/columns'
import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { toast } from '@/components/ui/use-toast'
import { useDeleteGoldenSql } from '@/hooks/api/useDeleteGoldenSql'
import useGoldenSqlList from '@/hooks/api/useGoldenSqlList'
import { ErrorResponse } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { Info } from 'lucide-react'
import Head from 'next/head'
import { FC, useCallback, useMemo, useState } from 'react'

const GoldenSQLPage: FC = () => {
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
  } = useGoldenSqlList()

  const [isRefreshing, setIsRefreshing] = useState(false)

  const deleteGoldenSql = useDeleteGoldenSql(mutate)

  const handleDelete = useCallback(
    async (id: string) => {
      try {
        await deleteGoldenSql(id)
        toast({
          variant: 'success',
          title: 'Golden SQL Removed',
          description:
            'This query was removed from the Golden SQL list and will not be used in further training.',
        })
      } catch (e) {
        console.error(e)
        const { message: title, trace_id: description } = e as ErrorResponse
        toast({
          variant: 'destructive',
          title,
          description,
          action: (
            <ToastAction altText="Try again" onClick={() => handleDelete(id)}>
              Try again
            </ToastAction>
          ),
        })
      }
    },
    [deleteGoldenSql],
  )

  const columns = useMemo(
    () => getColumns({ deleteAction: handleDelete }),
    [handleDelete],
  )

  const searchInfo = (
    <TooltipProvider>
      <Tooltip delayDuration={0}>
        <TooltipTrigger asChild>
          <Info size={18} className="text-slate-600" />
        </TooltipTrigger>
        <TooltipContent>
          Search Golden SQL queries by <strong>question</strong> or{' '}
          <strong>SQL</strong> fields.
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )

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
    pageContent = (
      <PageErrorMessage
        message="Something went wrong while fetching your organization Golden SQL queries."
        error={error}
      />
    )
  } else
    pageContent = (
      <DataTable
        id="golden-sql"
        columns={columns}
        data={items}
        enableColumnVisibility
        isLoadingFirst={isLoadingFirst}
        isRefreshing={isRefreshing}
        isLoadingMore={isLoadingMore}
        isReachingEnd={isReachingEnd}
        searchText={searchText}
        searchInfo={searchInfo}
        onSearchTextChange={setSearchText}
        onSearchTextClear={clearSearchText}
        onLoadMore={handleLoadMore}
        onRefresh={handleRefresh}
        noMoreDataMessage="No more queries"
      />
    )

  return (
    <PageLayout>
      <Head>
        <title>Golden SQL - Dataherald API</title>
      </Head>
      <div className="grow flex flex-col gap-4 m-6">
        <div className="flex flex-col gap-3 max-w-5xl">
          <p>
            When a query is marked as verified in the query editor, or manually
            uploaded through our API, it is stored as a{' '}
            <strong>Golden SQL Query</strong> and used to further train the
            model.
          </p>
          <p>
            To remove a query from the training set, delete it from the table
            below or mark it as <strong>“Not Verified”</strong> from the query
            editor.
          </p>
        </div>
        <ContentBox>{pageContent}</ContentBox>
      </div>
      <Toaster />
    </PageLayout>
  )
}

export default withPageAuthRequired(GoldenSQLPage)
