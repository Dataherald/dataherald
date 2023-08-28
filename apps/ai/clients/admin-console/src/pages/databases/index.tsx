import DatabaseError from '@/components/database/error'
import LoadingDatabase from '@/components/database/loading'
import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { TreeNode, TreeView } from '@/components/ui/tree-view'
import useDatabase from '@/hooks/api/useDatabase'
import { Database } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { Columns, Database as DatabaseIcon, Table2 } from 'lucide-react'
import { FC } from 'react'

const DatabasesPage: FC = () => {
  const { database, isLoading, error } = useDatabase()

  const mapDatabaseToTreeData = (database: Database): TreeNode => ({
    name: database.db_alias,
    icon: DatabaseIcon,
    children: [
      {
        name: 'tables',
        icon: Table2,
        children: database.tables.map((table) => ({
          name: table.name,
          icon: Table2,
          children: [
            {
              name: 'columns',
              icon: Columns,
              children: table.columns.map((column) => ({
                name: column,
                icon: Columns,
              })),
            },
          ],
        })),
      },
    ],
  })

  let pageContent: JSX.Element = <></>

  if (error) {
    pageContent = <DatabaseError />
  } else if (isLoading) {
    pageContent = <LoadingDatabase />
  } else {
    pageContent = (
      <>
        <h1 className="capitalize font-semibold">Connected Database</h1>
        <TreeView data={mapDatabaseToTreeData(database as Database)} />
      </>
    )
  }
  return (
    <PageLayout>
      <div>
        <ContentBox>{pageContent}</ContentBox>
      </div>
    </PageLayout>
  )
}

export default withPageAuthRequired(DatabasesPage)
