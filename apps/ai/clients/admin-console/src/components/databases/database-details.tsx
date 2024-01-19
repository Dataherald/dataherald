import DatabaseResourceSheet from '@/components/databases/database-resource-sheet'
import DatabaseTree from '@/components/databases/database-tree'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import { TreeProvider, useTree } from '@/components/ui/tree-view-context'
import { toast } from '@/components/ui/use-toast'
import useSynchronizeSchemas from '@/hooks/api/useSynchronizeSchemas'
import { cn } from '@/lib/utils'
import { Database, ETableSyncStatus } from '@/models/api'
import { Loader, RefreshCw, ScanText } from 'lucide-react'
import React, { ComponentType, FC, useState } from 'react'

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
        title: 'Scanning queued',
        description: `${selectedNodes.size} table schemas were succesfully queued for scanning.`,
      })
      setIsSynchronizing(false)
      resetSyncSelection()
      try {
        await onRefresh(optimisticDatabaseUpdate)
      } catch (e) {
        console.error(e)
        toast({
          variant: 'destructive',
          title: 'Oops! Something went wrong.',
          description: 'There was a problem refreshing your Databases.',
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
        title: 'Oops! Something went wrong.',
        description:
          'There was a problem scanning your Database table schemas.',
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
        <h1 className="font-bold">Connected Databases</h1>
        <div className="flex gap-3">
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button
                disabled={
                  isSynchronizing || isRefreshing || selectedNodes.size === 0
                }
              >
                <ScanText size={18} className="mr-2" />
                {`Scan table ${
                  selectedNodes.size === 0
                    ? 'schemas'
                    : `${selectedNodes.size} ${
                        selectedNodes.size === 1 ? 'schema' : 'schemas'
                      }`
                }`}
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle className="flex items-center gap-2">
                  <ScanText size={18} />
                  Scan Databases
                </AlertDialogTitle>
                <AlertDialogDescription>
                  You are about to add{' '}
                  {`${selectedNodes.size} ${
                    selectedNodes.size === 1 ? 'table schema' : 'tables schemas'
                  }`}{' '}
                  to the scanning queue. This asynchronous process could take a
                  while to complete.
                </AlertDialogDescription>
                <AlertDialogDescription>
                  Do you wish to continue?
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleSynchronization}>
                  {isSynchronizing ? (
                    <>
                      <Loader size={18} className="mr-2 animate-spin" />
                      Scanning
                    </>
                  ) : (
                    <>
                      <ScanText size={18} className="mr-2" />
                      Scan
                    </>
                  )}
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
          <Button
            variant="ghost"
            disabled={isRefreshing || isSynchronizing}
            onClick={() => onRefresh()}
          >
            <RefreshCw
              size={18}
              className={cn('mr-2', isRefreshing ? 'animate-spin' : '')}
            />
            {isRefreshing ? 'Refreshing' : 'Refresh'}
          </Button>
        </div>
      </div>

      <DatabaseTree database={database}></DatabaseTree>
      <DatabaseResourceSheet></DatabaseResourceSheet>
      <Toaster />
    </>
  )
}

export default withDatabaseSelection(DatabaseDetails)
