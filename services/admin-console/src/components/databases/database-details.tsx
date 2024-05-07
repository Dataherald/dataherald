import DatabaseConnectionFormDialog from '@/components/databases/database-connection-form-dialog'
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
import { Separator } from '@/components/ui/separator'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
} from '@/components/ui/tooltip'
import { useGlobalTreeSelection } from '@/components/ui/tree-view-global-context'
import { toast } from '@/components/ui/use-toast'
import useSynchronizeSchemas, {
  ScanRequest,
} from '@/hooks/api/database-connection/useSynchronizeSchemas'
import { Databases, ETableSyncStatus, ErrorResponse } from '@/models/api'
import { TooltipTrigger } from '@radix-ui/react-tooltip'
import { Loader, Plus, RefreshCcw, ScanText } from 'lucide-react'
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
              ...(globalSelection[db.db_connection_id].has(t.id)
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
              ...(globalSelection[db.db_connection_id].has(t.id)
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
      const scanRequestPayload: ScanRequest = {
        ids: Object.values(globalSelection).flatMap((selectedTables) =>
          Array.from(selectedTables.values()),
        ),
      }
      await synchronizeSchemas(scanRequestPayload)
      toast({
        variant: 'success',
        title: 'Scanning queued',
        description: `${globalSelectionSize} tables were succesfully queued for scanning.`,
      })
      triggerReset()
      setIsSynchronizing(false)
      try {
        await onRefresh(optimisticDatabasesUpdate)
      } catch (e) {
        console.error(e)
        const { message: title, trace_id: description } = e as ErrorResponse
        toast({
          variant: 'destructive',
          title,
          description,
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
      const { message: title, trace_id: description } = e as ErrorResponse
      toast({
        variant: 'destructive',
        title,
        description,
        action: (
          <ToastAction altText="Try again" onClick={handleSynchronization}>
            Try again
          </ToastAction>
        ),
      })
      onUpdateDatabasesData(databases)
    } finally {
      setIsSynchronizing(false)
    }
  }

  return (
    <>
      <TooltipProvider>
        <div className="flex items-center justify-between bg-slate-50 py-0">
          <h1 className="font-semibold">Connected Databases</h1>
          <div className="flex gap-1">
            <div className="flex items-center text-xs">
              {isSynchronizing ? (
                <div className="flex items-center gap-2 text-sky-500">
                  <Loader size={16} className="animate-spin" />
                  Preparing scan queue
                </div>
              ) : (
                <span className="text-slate-500">
                  {globalSelectionSize === 0
                    ? 'No tables selected'
                    : globalSelectionSize === 1
                    ? '1 table selected'
                    : `${globalSelectionSize} tables selected`}
                </span>
              )}
            </div>
            <AlertDialog>
              <Tooltip delayDuration={100}>
                <TooltipTrigger asChild>
                  <AlertDialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      disabled={
                        isSynchronizing ||
                        isRefreshing ||
                        globalSelectionSize === 0
                      }
                    >
                      <ScanText size={18} />
                    </Button>
                  </AlertDialogTrigger>
                </TooltipTrigger>
                <TooltipContent>Scan selected tables</TooltipContent>
              </Tooltip>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle className="flex items-center gap-2">
                    <ScanText size={16} />
                    Scan Databases
                  </AlertDialogTitle>
                  <AlertDialogDescription>
                    You are about to add{' '}
                    {`${globalSelectionSize} ${
                      globalSelectionSize === 1
                        ? 'table schema'
                        : 'tables schemas'
                    }`}{' '}
                    to the scanning queue. This asynchronous process could take
                    a while to complete.
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
                        <Loader size={16} className="mr-2 animate-spin" />
                        Scanning
                      </>
                    ) : (
                      'Scan'
                    )}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
            <div className="mx-2 flex items-center">
              <Separator orientation="vertical" className="bg-slate-400 h-5" />
            </div>
            <div className="flex gap-0">
              <Tooltip delayDuration={100}>
                <DatabaseConnectionFormDialog
                  onConnected={onRefresh}
                  renderTrigger={() => (
                    <TooltipTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <Plus size={16} strokeWidth={2} />
                      </Button>
                    </TooltipTrigger>
                  )}
                />
                <TooltipContent>Add Database</TooltipContent>
              </Tooltip>
              <Tooltip delayDuration={100}>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    disabled={isRefreshing || isSynchronizing}
                    onClick={() => onRefresh()}
                  >
                    <RefreshCcw
                      size={16}
                      className={isRefreshing ? 'animate-spin' : ''}
                    />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Refresh</TooltipContent>
              </Tooltip>
            </div>
          </div>
        </div>
      </TooltipProvider>

      <DatabasesTree databases={databases} />

      <Toaster />
    </>
  )
}

export default DatabaseDetails
