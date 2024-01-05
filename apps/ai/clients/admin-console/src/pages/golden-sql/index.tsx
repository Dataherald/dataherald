import { DataTable } from '@/components/data-table/data-table'
import { LoadingTable } from '@/components/data-table/loading-table'
import { getColumns } from '@/components/golden-sql/columns'
import PageLayout from '@/components/layout/page-layout'
import QueriesError from '@/components/queries/error'
import { ContentBox } from '@/components/ui/content-box'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import { toast } from '@/components/ui/use-toast'
import { useDeleteGoldenSql } from '@/hooks/api/useDeleteGoldenSql'
import useGoldenSqlList from '@/hooks/api/useGoldenSqlList'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { FC, useCallback, useMemo } from 'react'

const GoldenSQLPage: FC = () => {
  const {
    items = [],
    isLoadingFirst,
    isLoadingMore,
    isReachingEnd,
    error,
    page,
    setPage,
    mutate,
  } = useGoldenSqlList()
  const deleteGoldenSql = useDeleteGoldenSql(mutate)
  const handleDelete = useCallback(
    async (id: string) => {
      try {
        await deleteGoldenSql(id)
        toast({
          title: 'Golden SQL Removed',
          description:
            'This query was removed from the Golden SQL list and will not be used in further training.',
        })
      } catch (e) {
        console.error(e)
        toast({
          variant: 'destructive',
          title: 'Oops! Something went wrong.',
          description:
            'There was a problem with deleting your golden sql query',
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

  const handleLoadMore = () => {
    if (!isLoadingMore) {
      setPage(page + 1)
    }
  }

  let pageContent: JSX.Element = <></>

  if (error) {
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
        onLoadMore={handleLoadMore}
        noMoreDataMessage="No more queries"
      />
    )

  return (
    <PageLayout>
      <div className="grow flex flex-col gap-4 m-6">
        <div className="flex flex-col gap-3">
          <p className="max-w-5xl">
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
        <ContentBox className="overflow-auto">
          <div className="flex flex-col gap-3 bg-gray-50 py-0">
            <h1 className="font-bold">Training Queries</h1>
          </div>
          {pageContent}
        </ContentBox>
      </div>
      <Toaster />
    </PageLayout>
  )
}

export default withPageAuthRequired(GoldenSQLPage)
