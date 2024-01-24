import DatabasesTree from '@/components/databases/databases-tree'
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
import { useGlobalTreeSelection } from '@/components/ui/tree-view-global-context'
import { toast } from '@/components/ui/use-toast'
import useSynchronizeSchemas, {
  ScanRequest,
} from '@/hooks/api/useSynchronizeSchemas'
import { cn } from '@/lib/utils'
import { Databases, ETableSyncStatus } from '@/models/api'
import { Loader, RefreshCw, ScanText } from 'lucide-react'
import { FC, useState } from 'react'

interface DatabaseDetailsProps {
  databases: Databases
  isRefreshing: boolean
  onRefresh: (newData?: Databases) => Promise<void>
  onUpdateDatabasesData: (loadingData: Databases) => void
}

const DatabaseDetails: FC<DatabaseDetailsProps> = ({
  databases,
  isRefreshing,
  onRefresh,
  onUpdateDatabasesData,
}) => {
  const [isSynchronizing, setIsSynchronizing] = useState(false)
  const { globalSelection, globalSelectionSize, triggerReset } =
    useGlobalTreeSelection()
  const synchronizeSchemas = useSynchronizeSchemas()

  const handleSynchronization = async () => {
    setIsSynchronizing(true)
    const queuingScanningDatabases: Databases = databases.map((db) => {
      return globalSelection[db.db_connection_id]?.size > 0 // filter out db with empty selection
        ? {
            ...db,
            tables: db.tables.map((t) => ({
              ...t,
              ...(globalSelection[db.db_connection_id].has(t.name)
                ? {
                    sync_status: ETableSyncStatus.QUEUING_FOR_SCAN,
                    last_sync: null,
                    columns: [],
                  }
                : {}),
            })),
          }
        : db
    })
    onUpdateDatabasesData(queuingScanningDatabases)
    const optimisticDatabasesUpdate: Databases = databases.map((db) => {
      return globalSelection[db.db_connection_id]?.size > 0 // filter out db with empty selection
        ? {
            ...db,
            tables: db.tables.map((t) => ({
              ...t,
              ...(globalSelection[db.db_connection_id].has(t.name)
                ? {
                    sync_status: ETableSyncStatus.SYNCHRONIZING,
                    last_sync: null,
                    columns: [],
                  }
                : {}),
            })),
          }
        : db
    })
    try {
      const scanRequestPayload: ScanRequest = Object.keys(globalSelection)
        .filter((dbId) => globalSelection[dbId]?.size > 0)
        .map((dbId) => ({
          db_connection_id: dbId,
          table_names: Array.from(globalSelection[dbId]),
        }))
      await synchronizeSchemas(scanRequestPayload)
      toast({
        variant: 'success',
        title: 'Scanning queued',
        description: `${globalSelectionSize} table schemas were succesfully queued for scanning.`,
      })
      triggerReset()
      setIsSynchronizing(false)
      try {
        await onRefresh(optimisticDatabasesUpdate)
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
      onUpdateDatabasesData(databases)
      toast({
        variant: 'destructive',
        title: 'Oops! Something went wrong.',
        description:
          'There was a problem scanning your Databases table schemas.',
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
                  isSynchronizing || isRefreshing || globalSelectionSize === 0
                }
              >
                {isSynchronizing ? (
                  <>
                    <Loader size={18} className="mr-2 animate-spin" />
                    Preparing scan queue
                  </>
                ) : (
                  <>
                    <ScanText size={18} className="mr-2" />
                    {`Scan ${
                      globalSelectionSize === 0
                        ? 'table schemas'
                        : `${globalSelectionSize} table ${
                            globalSelectionSize === 1 ? 'schema' : 'schemas'
                          }`
                    }`}
                  </>
                )}
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
                  {`${globalSelectionSize} ${
                    globalSelectionSize === 1
                      ? 'table schema'
                      : 'tables schemas'
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

      <DatabasesTree databases={databases} />

      <Toaster />
    </>
  )
}

export default DatabaseDetails
