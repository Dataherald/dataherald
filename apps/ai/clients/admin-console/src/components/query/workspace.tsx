import QueryLastUpdated from '@/components/query/last-updated'
import LoadingQuery from '@/components/query/loading'
import LoadingBox from '@/components/query/loading-box'
import MessageSection from '@/components/query/message-section'
import QueryMetadata from '@/components/query/query-metadata'
import QueryQuestion from '@/components/query/question'
import {
  SectionHeader,
  SectionHeaderTitle,
} from '@/components/query/section-header'
import SqlEditor from '@/components/query/sql-editor'
import SqlResultsTable from '@/components/query/sql-results-table'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import { useToast } from '@/components/ui/use-toast'
import { QueryPatchRequest } from '@/hooks/api/query/useQueryPatch'
import {
  QUERY_STATUS_COLORS,
  QUERY_STATUS_EXPLANATION,
  formatQueryStatus,
  isNotVerified,
  isRejected,
  isVerified,
} from '@/lib/domain/query'
import { cn } from '@/lib/utils'
import { Query, QueryStatus } from '@/models/api'
import {
  EDomainQueryWorkspaceStatus,
  QueryWorkspaceStatus,
} from '@/models/domain'
import { Ban, Box, Code2, Loader, Play, Verified, XOctagon } from 'lucide-react'
import { FC, useEffect, useState } from 'react'

export const MAIN_ACTION_BTN_CLASSES = 'h-8 py-0 px-4 w-28'
export const SECONDARY_ACTION_BTN_CLASSES =
  'w-fit px-4 text-sm hover:bg-slate-300 hover:text-black/80 flex items-center gap-1'

const getWorkspaceQueryStatus = (status: QueryStatus) =>
  Object.values(EDomainQueryWorkspaceStatus).find((qs) => qs === status) ||
  EDomainQueryWorkspaceStatus.NOT_VERIFIED

export interface QueryWorkspaceProps {
  query: Query
  onResubmitQuery: () => Promise<Query | undefined>
  onExecuteQuery: (sql_query: string) => Promise<Query | undefined>
  onPatchQuery: (patches: QueryPatchRequest) => Promise<Query | undefined>
}

const QueryWorkspace: FC<QueryWorkspaceProps> = ({
  query,
  onResubmitQuery,
  onExecuteQuery,
  onPatchQuery,
}) => {
  const {
    id: queryId,
    display_id,
    question,
    question_date,
    response, // TODO delete this
    message,
    username,
    sql_query,
    sql_query_result,
    sql_error_message,
    evaluation_score,
    status,
    last_updated,
    updated_by,
  } = query

  const questionDate: Date = new Date(question_date)
  const lastUpdatedDate: Date = new Date(last_updated)

  const [currentSqlQuery, setCurrentSqlQuery] = useState(sql_query)
  const [currentQueryStatus, setCurrentQueryStatus] =
    useState<EDomainQueryWorkspaceStatus>(getWorkspaceQueryStatus(status))

  const [resubmittingQuery, setResubmittingQuery] = useState(false)
  const [runningQuery, setRunningQuery] = useState(false)
  const [updatingQueryStatus, setUpdatingQueryStatus] = useState(false)

  const { toast } = useToast()

  useEffect(() => setCurrentSqlQuery(sql_query), [sql_query])
  useEffect(
    () => setCurrentQueryStatus(getWorkspaceQueryStatus(status)),
    [status],
  )

  const handleResubmit = async () => {
    if (resubmittingQuery) return
    setResubmittingQuery(true)
    try {
      await onResubmitQuery()
      toast({
        title: 'Query updated',
        description:
          'The query was resubmitted to the platform for a new response',
      })
    } catch (error) {
      console.error(error)
      toast({
        variant: 'destructive',
        title: 'Ups! Something went wrong.',
        description: 'There was a problem with resubmitting the query',
        action: (
          <ToastAction altText="Try again" onClick={handleResubmit}>
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setResubmittingQuery(false)
    }
  }

  const handleRunQuery = async () => {
    if (runningQuery) return
    setRunningQuery(true)
    try {
      await onExecuteQuery(currentSqlQuery)
      toast({
        title: 'Query updated',
        description:
          'The query was executed successfully and the results were updated',
      })
    } catch (e) {
      console.error(e)
      toast({
        variant: 'destructive',
        title: 'Ups! Something went wrong.',
        description: 'There was a problem with running the query',
        action: (
          <ToastAction altText="Try again" onClick={handleRunQuery}>
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setRunningQuery(false)
    }
  }

  const updateQueryStatus = async (newStatus: EDomainQueryWorkspaceStatus) => {
    if (updatingQueryStatus) return
    setUpdatingQueryStatus(true)
    try {
      await onPatchQuery({
        query_status: newStatus,
      })
      if (isVerified(newStatus)) {
        toast({
          variant: 'success',
          title: 'Query Verified',
          description:
            'Query added to the Golden SQL training set and used to further train the model for future queries',
        })
      } else if (isNotVerified(newStatus)) {
        toast({
          title: 'Query Unverified',
          description:
            'The query is not part of the Golden SQL training set and not used to improve the platform accuracy',
        })
      } else if (isRejected(newStatus)) {
        toast({
          variant: 'destructive-outline',
          title: 'Query Rejected',
          description:
            'The query is marked as rejected and will not be used to improve the platform accuracy',
        })
      }
    } catch (e) {
      console.error(e)
      setCurrentQueryStatus(getWorkspaceQueryStatus(status))
      toast({
        variant: 'destructive',
        title: 'Ups! Something went wrong.',
        description: 'There was a problem with updating the query status',
        action: (
          <ToastAction
            altText="Try again"
            onClick={() => updateQueryStatus(newStatus)}
          >
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setUpdatingQueryStatus(false)
    }
  }

  const handleSqlChange = (value: string) => {
    setCurrentSqlQuery(value)
  }

  const handleQueryStatusChange = (value: EDomainQueryWorkspaceStatus) => {
    setCurrentQueryStatus(value)
    updateQueryStatus(value)
  }

  return (
    <>
      <div
        className="grow flex flex-col gap-3 mt-4 overflow-auto"
        data-ph-capture-attribute-query_id={queryId}
        data-ph-capture-attribute-asker={username}
      >
        <div id="header" className="flex items-end justify-between gap-3 px-6">
          <QueryQuestion
            className="max-w-2xl"
            {...{ username, question, questionDate }}
          />
          <QueryMetadata
            {...{
              queryId: display_id,
              status,
              updatingQuery:
                runningQuery || updatingQueryStatus || resubmittingQuery,
              confidenceLevel: evaluation_score,
              onResubmit: handleResubmit,
            }}
          />
        </div>
        {resubmittingQuery ? (
          <LoadingQuery enableHeader={false} />
        ) : (
          <div className="grow flex flex-col overflow-auto">
            <SectionHeader>
              <SectionHeaderTitle>
                <Code2 strokeWidth={2}></Code2>
                {isNotVerified(currentQueryStatus) ? 'Verify SQL' : 'SQL'}
              </SectionHeaderTitle>
              {isNotVerified(currentQueryStatus) && (
                <Button
                  onClick={handleRunQuery}
                  disabled={runningQuery || updatingQueryStatus}
                  className={cn(MAIN_ACTION_BTN_CLASSES)}
                >
                  {runningQuery ? (
                    <>
                      <Loader
                        className="mr-2 animate-spin"
                        size={16}
                        strokeWidth={2.5}
                      />{' '}
                      Running
                    </>
                  ) : (
                    <>
                      <Play className="mr-2" size={16} strokeWidth={2.5} />
                      Run
                    </>
                  )}
                </Button>
              )}
            </SectionHeader>
            <div className="grow flex flex-col gap-2 px-6 py-4">
              <div className="grow h-44">
                <SqlEditor
                  disabled={isVerified(currentQueryStatus)}
                  query={currentSqlQuery}
                  onValueChange={handleSqlChange}
                />
              </div>
              <QueryLastUpdated
                responsible={updated_by?.name as string}
                date={lastUpdatedDate}
              />
              {runningQuery || updatingQueryStatus ? (
                <div id="loading_query_results" className="shrink-0 h-32">
                  <LoadingBox />
                </div>
              ) : isVerified(currentQueryStatus) ? (
                <div
                  id="verified_banner"
                  className="shrink-0 h-32 flex flex-col border bg-muted text-muted-foreground"
                >
                  <div className="h-full flex flex-col items-center justify-center gap-2">
                    <div className="flex items-center gap-2 text-green-700">
                      <Verified size={18} strokeWidth={2} /> Verified query
                    </div>
                    <div className="px-20 text-center">
                      {`The SQL query was verified and added to the Golden SQL training set. To modify the SQL query, please set the status to "Not Verified" first.`}
                    </div>
                  </div>
                </div>
              ) : isRejected(currentQueryStatus) ? (
                <div
                  id="rejected__banner"
                  className="shrink-0 h-32 flex flex-col border bg-muted text-red-500"
                >
                  <div className="h-full flex items-center justify-center gap-2 ">
                    <Ban size={18} strokeWidth={2} /> Rejected query
                  </div>
                </div>
              ) : sql_error_message ? (
                <div className="shrink-0 h-32 flex flex-col items-center border bg-white border-red-600 text-red-600">
                  <div className="flex items-center gap-3 py-5 font-bold">
                    <XOctagon size={28} />
                    <span>SQL Error</span>
                  </div>
                  <div className="w-full overflow-auto px-8 pb-3">
                    {sql_error_message}
                  </div>
                </div>
              ) : (
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
            </div>
            <MessageSection
              {...{
                queryId,
                initialMessage: message || response,
                onPatchQuery,
              }}
            />
            <SectionHeader>
              <SectionHeaderTitle>
                <Box strokeWidth={2}></Box>Query Status
              </SectionHeaderTitle>
            </SectionHeader>
            <div className="p-6 flex flex-col gap-5">
              <RadioGroup
                disabled={runningQuery || updatingQueryStatus}
                className="space-y-1"
                value={currentQueryStatus}
                onValueChange={handleQueryStatusChange}
              >
                {Object.values(EDomainQueryWorkspaceStatus).map(
                  (qs: QueryWorkspaceStatus, idx) => (
                    <div
                      key={qs + idx}
                      className={cn(
                        'flex items-center space-x-2',
                        QUERY_STATUS_COLORS[qs].text,
                        qs === currentQueryStatus && 'font-bold',
                      )}
                    >
                      <RadioGroupItem
                        value={qs}
                        id={qs}
                        className={cn(
                          QUERY_STATUS_COLORS[qs].text,
                          QUERY_STATUS_COLORS[qs].border,
                        )}
                      />
                      <Label
                        htmlFor={qs}
                        className={cn(
                          'tracking-wide text-base',
                          runningQuery || updatingQueryStatus
                            ? ''
                            : 'cursor-pointer',
                        )}
                      >
                        {formatQueryStatus(qs)}{' '}
                        <span className="ml-2 text-xs text-slate-400">
                          {QUERY_STATUS_EXPLANATION[qs]}
                        </span>
                      </Label>
                    </div>
                  ),
                )}
              </RadioGroup>
            </div>
          </div>
        )}
      </div>
      <Toaster />
    </>
  )
}

export default QueryWorkspace
