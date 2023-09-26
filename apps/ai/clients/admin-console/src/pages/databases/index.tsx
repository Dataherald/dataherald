import DatabaseConnection from '@/components/databases/database-connection'
import DatabasesError from '@/components/databases/error'
import LoadingDatabases from '@/components/databases/loading'
import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { TreeNode, TreeView } from '@/components/ui/tree-view'
import { TreeProvider } from '@/components/ui/tree-view-context'
import useDatabases from '@/hooks/api/useDatabases'
import { Databases } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { Columns, Database as DatabaseIcon, Table2 } from 'lucide-react'
import { FC, useEffect, useState } from 'react'

const mapDatabaseToTreeData = (databases: Databases): TreeNode => ({
  id: 'root',
  name: 'Databases',
  icon: DatabaseIcon,
  children: databases.map((database) => ({
    id: database.alias,
    name: database.alias,
    icon: DatabaseIcon,
    selectable: true,
    children: [
      {
        name: 'Tables',
        id: 'tables-root',
        icon: Table2,
        children: database.tables.map((table) => ({
          id: table.name,
          name: table.name,
          icon: Table2,
          selectable: true,
          children: table.columns?.length
            ? [
                {
                  id: 'columns-root',
                  name: 'Columns',
                  icon: Columns,
                  children: table.columns.map((column) => ({
                    id: column,
                    name: column,
                    icon: Columns,
                  })),
                },
              ]
            : [],
        })),
      },
    ],
  })),
})

const DatabasesPage: FC = () => {
  const { databases, isLoading, error, mutate } = useDatabases()
  const [connectingDB, setConnectingDB] = useState<boolean | null>(null)

  const handleDatabaseConnected = () => mutate()
  const handleDatabaseConnectionFinish = () => {
    if (databases?.length !== 0) setConnectingDB(false)
  }

  useEffect(() => {
    if (databases?.length === 0 && connectingDB === null) {
      setConnectingDB(true)
    }
  }, [databases, connectingDB])

  let pageContent: JSX.Element = <></>

  if (error) {
    pageContent = <DatabasesError />
  } else if (isLoading) {
    pageContent = <LoadingDatabases />
  } else if (connectingDB) {
    pageContent = (
      <DatabaseConnection
        onConnected={handleDatabaseConnected}
        onFinish={handleDatabaseConnectionFinish}
      />
    )
  } else {
    pageContent = (
      <>
        <h1 className="capitalize font-semibold">Connected Databases</h1>
        <TreeProvider>
          <TreeView rootNode={mapDatabaseToTreeData(databases as Databases)} />
        </TreeProvider>
      </>
    )
  }
  return (
    <PageLayout>
      <ContentBox>{pageContent}</ContentBox>
    </PageLayout>
  )
}

export default withPageAuthRequired(DatabasesPage)
