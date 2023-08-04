import QueryLastUpdated from '@/components/query/last-updated'
import LoadingQueryResults from '@/components/query/loading-results'
import QueryProcess from '@/components/query/process'
import QueryQuestion from '@/components/query/question'
import SqlEditor from '@/components/query/sql-editor'
import SqlResultsTable from '@/components/query/sql-results-table'
import QueryVerifySelect from '@/components/query/verify-select'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Query, QueryStatus } from '@/models/api'
import { Database, ListOrdered, Play, Save, XOctagon } from 'lucide-react'
import Link from 'next/link'
import { FC, useState } from 'react'

export interface QueryWorkspaceProps {
  query: Query
  onExecuteQuery: (sql_query: string) => void
}

const QueryWorkspace: FC<QueryWorkspaceProps> = ({ query, onExecuteQuery }) => {
  const {
    question,
    question_date,
    nl_response,
    user: { name: username },
    sql_query,
    sql_query_result,
    sql_error_message,
    status,
    ai_process,
    last_updated,
  } = query

  const questionDate: Date = new Date(question_date)
  const lastUpdatedDate: Date = new Date(last_updated)
  const [currentSqlQuery, setCurrentSqlQuery] = useState(sql_query)
  const [verifiedStatus, setVerifiedStatus] = useState<QueryStatus>(status)
  const [loadingQueryResults, setLoadingQueryResults] = useState(false)

  const handleSqlChange = (value: string) => {
    setCurrentSqlQuery(value)
  }

  const handleVerifyChange = (verifiedStatus: QueryStatus) => {
    setVerifiedStatus(verifiedStatus)
  }

  const handleRunClick = async () => {
    setLoadingQueryResults(true)
    await onExecuteQuery(currentSqlQuery)
    setLoadingQueryResults(false)
  }

  return (
    <div className="grow flex flex-col gap-5">
      <div id="header" className="flex justify-between gap-3">
        <QueryQuestion {...{ username, question, questionDate }} />
        <div className="flex items-center gap-5">
          <Link href="/queries">
            <Button variant="link" className="font-normal">
              Cancel
            </Button>
          </Link>
          <Button variant="primary" className="px-6">
            <Save className="mr-2" size={20} strokeWidth={2.5} /> Save
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
                  <Database className="mr-2" size={20} strokeWidth={2.5} /> SQL
                </TabsTrigger>
                <TabsTrigger value="process">
                  <ListOrdered className="mr-2" size={20} strokeWidth={2.5} />
                  Process
                </TabsTrigger>
              </div>
              <div id="actions" className="flex items-center gap-5">
                <span className="text-lg">Mark as </span>
                <QueryVerifySelect
                  verifiedStatus={verifiedStatus}
                  onValueChange={handleVerifyChange}
                />
                <Button onClick={handleRunClick}>
                  <Play className="mr-2" size={20} strokeWidth={2.5} /> Run
                </Button>
              </div>
            </div>
          </TabsList>
          <TabsContent value="sql" className="pt-3 grow">
            <SqlEditor
              initialQuery={currentSqlQuery}
              onValueChange={handleSqlChange}
            />
          </TabsContent>
          <TabsContent value="process" className="pt-3 grow overflow-auto">
            <QueryProcess processSteps={ai_process} />
          </TabsContent>
        </Tabs>
        <QueryLastUpdated date={lastUpdatedDate} />
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
        <div className="flex flex-col gap-3">
          <div
            id="query_results"
            className="min-h-[12rem] max-h-80 flex flex-col border bg-white"
          >
            {sql_query_result === null ? (
              <div className="w-full h-60 flex items-center justify-center bg-gray-100">
                <div className="text-gray-600">No Results</div>
              </div>
            ) : (
              <SqlResultsTable
                columns={sql_query_result.columns.map((columnKey: string) => ({
                  id: columnKey,
                  header: columnKey,
                  accessorKey: columnKey,
                }))}
                data={sql_query_result.rows}
              />
            )}
          </div>
          {sql_query_result && (
            <div id="nl_response">
              <span className="font-bold mr-1">Answer:</span>
              {nl_response}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default QueryWorkspace
