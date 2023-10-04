import CustomResponseDialog from '@/components/query/custom-response-dialog'
import QueryLastUpdated from '@/components/query/last-updated'
import LoadingQueryResults from '@/components/query/loading-results'
import QueryProcess from '@/components/query/process'
import QueryQuestion from '@/components/query/question'
import SqlEditor from '@/components/query/sql-editor'
import SqlResultsTable from '@/components/query/sql-results-table'
import QueryVerifySelect from '@/components/query/verify-select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import { useToast } from '@/components/ui/use-toast'
import { isNotVerified, isRejected, isVerified } from '@/lib/domain/query'
import { Query, QueryStatus } from '@/models/api'
import {
  AlertCircle,
  Ban,
  Database,
  Edit,
  ListOrdered,
  Loader,
  Play,
  Save,
  XOctagon,
} from 'lucide-react'
import Link from 'next/link'
import { FC, useEffect, useState } from 'react'

export interface QueryWorkspaceProps {
  query: Query
  onExecuteQuery: (sql_query: string) => void
  onPatchQuery: (patches: {
    sql_query: string
    custom_response: string
    query_status: QueryStatus
  }) => void
}

const QueryWorkspace: FC<QueryWorkspaceProps> = ({
  query,
  onExecuteQuery,
  onPatchQuery,
}) => {
  const {
    question,
    question_date,
    nl_response,
    username,
    sql_query,
    sql_query_result,
    sql_error_message,
    status,
    ai_process,
    last_updated,
    updated_by,
  } = query

  const questionDate: Date = new Date(question_date)
  const lastUpdatedDate: Date = new Date(last_updated)
  const [currentSqlQuery, setCurrentSqlQuery] = useState(sql_query)
  const [verificationStatus, setVerifiedStatus] = useState<QueryStatus>(status)
  const [textResponse, setCustomResponse] = useState<string>(nl_response)
  const [textResponseHasChanges, setTextResponseHasChanges] = useState(false)
  const [openEditResponseDialog, setOpenEditResponseDialog] = useState(false)
  const [savingQuery, setSavingQuery] = useState(false)
  const [loadingQueryResults, setLoadingQueryResults] = useState(false)

  const { toast } = useToast()

  const handleRunQuery = async () => {
    setLoadingQueryResults(true)
    try {
      await onExecuteQuery(currentSqlQuery)
      toast({
        variant: 'success',
        title: 'Query executed',
        description:
          'The results table and the natural language answer were updated.',
      })
    } catch (e) {
      console.error(e)
      toast({
        variant: 'destructive',
        title: 'Ups! Something went wrong.',
        description: 'There was a problem with running your query',
        action: (
          <ToastAction altText="Try again" onClick={handleRunQuery}>
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setLoadingQueryResults(false)
    }
  }

  const handleSaveQuery = async () => {
    try {
      setSavingQuery(true)
      await onPatchQuery({
        query_status: verificationStatus,
        custom_response: textResponse,
        sql_query: currentSqlQuery,
      })
      if (isVerified(verificationStatus)) {
        toast({
          variant: 'success',
          title: 'Verified',
          description: (
            <p>
              Response sent to the Slack thread and added to the Golden SQL
              training set.
            </p>
          ),
        })
      } else if (isNotVerified(verificationStatus)) {
        toast({
          title: 'Marked as Unverified',
          description:
            'Removed from the Golden SQL list and not used in further training.',
        })
      } else if (isRejected(verificationStatus)) {
        toast({
          title: 'Rejected',
          description:
            'Response sent to the Slack thread informing that this query could not be answered.',
        })
      }
    } catch (e) {
      console.error(e)
      toast({
        variant: 'destructive',
        title: 'Ups! Something went wrong.',
        description: 'There was a problem with saving your query',
        action: (
          <ToastAction altText="Try again" onClick={handleSaveQuery}>
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setSavingQuery(false)
    }
  }

  const handleSqlChange = (value: string) => {
    setCurrentSqlQuery(value)
  }

  const handleVerifyChange = (verificationStatus: QueryStatus) => {
    setVerifiedStatus(verificationStatus)
    if (isRejected(verificationStatus) && !textResponseHasChanges) {
      setOpenEditResponseDialog(true)
    }
  }

  const handleCloseEditDialog = (newCustomResponse = textResponse) => {
    setCustomResponse(newCustomResponse)
    setOpenEditResponseDialog(false)
  }

  useEffect(() => {
    setTextResponseHasChanges(textResponse !== nl_response)
  }, [nl_response, textResponse])

  const rejectedBanner = (
    <div className="h-full flex items-center justify-center gap-2 text-muted-foreground">
      <Ban size={18} strokeWidth={2} /> Rejected query
    </div>
  )

  return (
    <>
      <div className="grow flex flex-col gap-5">
        <div id="header" className="flex justify-between gap-3">
          <QueryQuestion {...{ username, question, questionDate }} />
          <div className="flex items-center self-start gap-5">
            <Link href="/queries">
              <Button variant="link" className="font-normal">
                Cancel
              </Button>
            </Link>
            <Button
              variant="primary"
              className="px-6"
              onClick={handleSaveQuery}
              disabled={savingQuery}
            >
              {savingQuery ? (
                <>
                  <Loader
                    className="mr-2 animate-spin"
                    size={20}
                    strokeWidth={2.5}
                  />{' '}
                  Saving
                </>
              ) : (
                <>
                  <Save className="mr-2" size={20} strokeWidth={2.5} /> Save
                </>
              )}
            </Button>
          </div>
        </div>
        <div
          id="tabs"
          className="shrink-0 h-80 grow flex-auto flex flex-col gap-5 bg-white border rounded-xl px-6 py-4"
        >
          <Tabs
            defaultValue="sql"
            className="w-full grow overflow-auto flex flex-col"
          >
            <TabsList className="w-full">
              <div className="w-full flex gap-3 justify-between py-2">
                <div id="tab-triggers" className="flex gap-5">
                  <TabsTrigger value="sql">
                    <Database className="mr-2" size={20} strokeWidth={2.5} />{' '}
                    SQL
                  </TabsTrigger>
                  <TabsTrigger value="process">
                    <ListOrdered className="mr-2" size={20} strokeWidth={2.5} />
                    Process
                  </TabsTrigger>
                </div>
                <div id="actions" className="flex items-center gap-5">
                  <span className="text-lg">Mark as </span>
                  <QueryVerifySelect
                    verificationStatus={verificationStatus}
                    onValueChange={handleVerifyChange}
                  />
                  <Button
                    onClick={handleRunQuery}
                    disabled={
                      loadingQueryResults || isRejected(verificationStatus)
                    }
                  >
                    {loadingQueryResults ? (
                      <>
                        <Loader
                          className="mr-2 animate-spin"
                          size={20}
                          strokeWidth={2.5}
                        />{' '}
                        Running
                      </>
                    ) : (
                      <>
                        <Play className="mr-2" size={20} strokeWidth={2.5} />
                        Run
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </TabsList>
            <TabsContent value="sql" className="pt-3 grow">
              {isRejected(verificationStatus) ? (
                rejectedBanner
              ) : (
                <SqlEditor
                  initialQuery={currentSqlQuery}
                  onValueChange={handleSqlChange}
                />
              )}
            </TabsContent>
            <TabsContent value="process" className="pt-3 grow overflow-auto">
              {isRejected(verificationStatus) ? (
                rejectedBanner
              ) : (
                <QueryProcess processSteps={ai_process} />
              )}
            </TabsContent>
          </Tabs>
          <QueryLastUpdated
            responsible={updated_by?.name as string}
            date={lastUpdatedDate}
          />
        </div>
        {loadingQueryResults ? (
          <div className="shrink-0 h-60">
            <LoadingQueryResults />
          </div>
        ) : sql_error_message ? (
          <div className="shrink-0 h-60 flex flex-col items-center bg-white border border-red-600 text-red-600">
            <div className="flex items-center gap-3 py-5 font-bold">
              <XOctagon size={28} />
              <span>SQL Error</span>
            </div>
            <div className="w-full overflow-auto px-8 pb-3">
              {sql_error_message}
            </div>
          </div>
        ) : (
          <>
            {!isRejected(verificationStatus) && (
              <div
                id="query_results"
                className="min-h-[10rem] max-h-80 flex flex-col border bg-white"
              >
                {sql_query_result === null ? (
                  <div className="w-full h-44 flex items-center justify-center bg-gray-100">
                    <div className="text-gray-600">No Results</div>
                  </div>
                ) : (
                  <SqlResultsTable
                    columns={sql_query_result.columns.map(
                      (columnKey: string) => ({
                        id: columnKey,
                        header: columnKey,
                        accessorKey: columnKey,
                      }),
                    )}
                    data={sql_query_result.rows}
                  />
                )}
              </div>
            )}
            {textResponse && (
              <>
                <div className="flex items-start justify-between gap-3">
                  <div id="text-response" className="pt-2">
                    <span className="font-bold mr-1">
                      {isRejected(verificationStatus)
                        ? 'Rejection reason:'
                        : 'Answer:'}
                    </span>
                    <span className="break-words">{textResponse}</span>
                  </div>
                  <Button
                    variant="link"
                    className="font-normal text-black flex items-center gap-1 py-2 p-0 min-w-fit"
                    onClick={() => setOpenEditResponseDialog(true)}
                  >
                    <Edit size={18} strokeWidth={2}></Edit>
                    Edit
                  </Button>
                </div>
                {(isVerified(verificationStatus) ||
                  isRejected(verificationStatus)) && (
                  <Alert variant="info" className="flex items-center gap-2">
                    <div>
                      <AlertCircle size={18} />
                    </div>
                    <AlertDescription>
                      {`This message will be sent as the question's response to
                      the Slack thread each time you save.`}
                    </AlertDescription>
                  </Alert>
                )}
              </>
            )}
          </>
        )}
      </div>
      {isRejected(verificationStatus) ? (
        <CustomResponseDialog
          title={
            <div className="flex items-center gap-2">
              <Ban size={18} strokeWidth={3}></Ban> Rejection Reason
            </div>
          }
          description="Describe the reason for rejecting the query"
          isOpen={openEditResponseDialog}
          initialValue={textResponse}
          onClose={handleCloseEditDialog}
        ></CustomResponseDialog>
      ) : (
        <CustomResponseDialog
          title={
            <div className="flex items-center gap-2">
              <Edit size={18} strokeWidth={3}></Edit> Edit Response
            </div>
          }
          description="Compose the response for the question"
          isOpen={openEditResponseDialog}
          initialValue={textResponse}
          onClose={handleCloseEditDialog}
        ></CustomResponseDialog>
      )}
      <Toaster />
    </>
  )
}

export default QueryWorkspace
