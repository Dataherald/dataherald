import { columns } from '@/components/queries/columns'
import { DataTable } from '@/components/queries/data-table'
import QueriesError from '@/components/queries/error'
import QueriesLayout from '@/components/queries/layout'
import { LoadingTable } from '@/components/queries/loading'
import useQueries from '@/hooks/api/useQueries'

export default function QueriesPage() {
  const { queries, loading, error } = useQueries()

  let pageContent: JSX.Element = <></>

  if (loading) {
    pageContent = <LoadingTable columnLength={columns.length} rowLength={10} />
  }

  if (error) {
    pageContent = <QueriesError />
  }

  if (queries) {
    pageContent = <DataTable columns={columns} data={queries || []} />
  }

  return (
    <QueriesLayout>
      <h1 className="font-bold">Latest Queries</h1>
      {pageContent}
    </QueriesLayout>
  )
}
