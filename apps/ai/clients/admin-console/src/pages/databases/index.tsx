import DatabaseConnection from '@/components/databases/database-connection'
import DatabasesError from '@/components/databases/error'
import LoadingDatabases from '@/components/databases/loading'
import PageLayout from '@/components/layout/page-layout'
import { Button } from '@/components/ui/button'
import { ContentBox } from '@/components/ui/content-box'
import { TreeNode, TreeView } from '@/components/ui/tree-view'
import { TreeProvider } from '@/components/ui/tree-view-context'
import useDatabases from '@/hooks/api/useDatabases'
import {
  formatSchemaStatus,
  getDomainSchemaStatusColor,
  getDomainSchemaStatusIcon,
  isSelectableByStatus,
} from '@/lib/domain/database'
import { cn, renderIcon } from '@/lib/utils'
import { Databases } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { formatDistance } from 'date-fns'
import {
  Columns,
  Database as DatabaseIcon,
  RefreshCw,
  Table2,
} from 'lucide-react'
import { FC, useEffect, useState } from 'react'

const mapDatabaseToTreeData = (databases: Databases): TreeNode => ({
  id: 'root',
  name: 'Databases',
  icon: DatabaseIcon,
  children: databases.map((database) => ({
    id: database.alias,
    name: database.alias,
    icon: DatabaseIcon,
    selectable: !database.tables.find(
      (table) => !isSelectableByStatus(table.status),
    ),
    children: [
      {
        name: 'Tables',
        id: 'tables-root',
        icon: Table2,
        children: database.tables.map((table) => ({
          id: table.name,
          name: table.name,
          icon: Table2,
          selectable: isSelectableByStatus(table.status),
          slot: (
            <div
              className={cn(
                'flex items-center gap-2 text-sm',
                getDomainSchemaStatusColor(table.status),
              )}
            >
              <div className="flex items-center gap-3 min-w-fit px-5">
                {renderIcon(getDomainSchemaStatusIcon(table.status), {
                  size: 16,
                  strokeWidth: 2,
                })}
                <span className="capitalize">
                  {formatSchemaStatus(table.status)}
                </span>
                {table.last_schemas_sync && (
                  <span className="text-gray-400">
                    {formatDistance(
                      new Date(table.last_schemas_sync),
                      new Date(),
                      { addSuffix: true },
                    )}
                  </span>
                )}
              </div>
            </div>
          ),
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
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [connectingDB, setConnectingDB] = useState<boolean | null>(null)

  const handleDatabaseConnected = () => mutate()
  const handleDatabaseConnectionFinish = () => {
    if (databases?.length !== 0) setConnectingDB(false)
  }

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await mutate()
    setIsRefreshing(false)
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
        <div className="flex items-center justify-between bg-gray-50 py-0">
          <h1 className="font-bold">Connected Databases</h1>
          <Button
            variant="outline"
            className="bg-gray-50"
            disabled={isRefreshing}
            onClick={handleRefresh}
          >
            <RefreshCw
              size={18}
              className={cn('mr-2', isRefreshing ? 'animate-spin' : '')}
            />{' '}
            {!isRefreshing ? 'Refresh' : 'Refreshing'}
          </Button>
        </div>

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
