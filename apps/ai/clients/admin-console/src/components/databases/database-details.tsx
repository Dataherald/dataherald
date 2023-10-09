import { Button } from '@/components/ui/button'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import { TreeProvider, useTree } from '@/components/ui/tree-view-context'
import { toast } from '@/components/ui/use-toast'
import useSynchronizeSchemas from '@/hooks/api/useSynchronizeSchemas'
import { cn } from '@/lib/utils'
import { Database, ETableSyncStatus } from '@/models/api'
import { Loader, RefreshCw, UploadCloud } from 'lucide-react'
import React, { ComponentType, FC, useState } from 'react'
import DatabaseTree from './database-tree'

interface DatabaseDetailsProps {
  database: Database
  isRefreshing: boolean
  onRefresh: (newData?: Database) => Promise<void>
}

type WithDatabaseSelection = (
  Component: ComponentType<DatabaseDetailsProps>,
) => React.FC<DatabaseDetailsProps>

const withDatabaseSelection: WithDatabaseSelection = (Component) => {
  return function WithDatabaseSelection(
    props: DatabaseDetailsProps,
  ): JSX.Element {
    return (
      <TreeProvider>
        <Component {...props} />
      </TreeProvider>
    )
  }
}

const DatabaseDetails: FC<DatabaseDetailsProps> = ({
  database,
  isRefreshing,
  onRefresh,
}) => {
  const [isSynchronizing, setIsSynchronizing] = useState(false)
  const { selectedNodes, resetSelection } = useTree()
  const synchronizeSchemas = useSynchronizeSchemas()

  const resetSyncSelection = resetSelection

  const handleSynchronization = async () => {
    setIsSynchronizing(true)
    const optimisticDatabaseUpdate = {
      ...database,
      tables: database.tables.map((t) => ({
        ...t,
        ...(selectedNodes.has(t.name)
          ? {
              sync_status: ETableSyncStatus.SYNCHRONIZING,
              last_sync: null,
            }
          : {}),
      })),
    }
    try {
      await synchronizeSchemas({
        db_connection_id: database.db_connection_id,
        table_names: Array.from(selectedNodes),
      })
      toast({
        variant: 'success',
        title: 'Synchronization queued',
        description: `${selectedNodes.size} tables schemas were succesfully queued for synchronization.`,
      })
      setIsSynchronizing(false)
      resetSyncSelection()
      try {
        await onRefresh(optimisticDatabaseUpdate)
      } catch (e) {
        console.error(e)
        toast({
          variant: 'destructive',
          title: 'Ups! Something went wrong.',
          description: 'There was a problem refreshing your Database.',
          action: (
            <ToastAction
              altText="Try again"
              onClick={() => handleSynchronization()}
            >
              Try again
            </ToastAction>
          ),
        })
      }
    } catch (e) {
      console.error(e)
      toast({
        variant: 'destructive',
        title: 'Ups! Something went wrong.',
        description:
          'There was a problem synchronizing your Database tables schemas.',
        action: (
          <ToastAction altText="Try again" onClick={handleSynchronization}>
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setIsSynchronizing(false)
    }
  }

  return (
    <>
      <div className="flex items-center justify-between bg-gray-50 py-0">
        <h1 className="font-bold">Connected Database</h1>
        <div className="flex gap-3">
          <Button
            disabled={
              isSynchronizing || isRefreshing || selectedNodes.size === 0
            }
            onClick={handleSynchronization}
          >
            {isSynchronizing ? (
              <Loader size={18} className="mr-2 animate-spin" />
            ) : (
              <UploadCloud size={18} className="mr-2" />
            )}
            {`${isSynchronizing ? `Synchronizing` : 'Synchronize'} ${
              selectedNodes.size
            } tables schemas`}
          </Button>
          <Button
            variant="outline"
            className="bg-gray-50"
            disabled={isRefreshing || isSynchronizing}
            onClick={() => onRefresh()}
          >
            <RefreshCw
              size={18}
              className={cn('mr-2', isRefreshing ? 'animate-spin' : '')}
            />{' '}
            {isRefreshing ? 'Refreshing' : 'Refresh'}
          </Button>
        </div>
      </div>

      <DatabaseTree database={database}></DatabaseTree>
      <Toaster />
    </>
  )
}

export default withDatabaseSelection(DatabaseDetails)
