import QueryProcess from '@/components/query/./process'
import QueryQuestion from '@/components/query//question'
import SqlResultsTable from '@/components/query//sql-results-table'
import QueryLastUpdated from '@/components/query/last-updated'
import SqlEditor from '@/components/query/sql-editor'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Query, QueryStatus } from '@/models/api'
import { Database, ListOrdered, Play, Save } from 'lucide-react'
import Link from 'next/link'
import { FC, useState } from 'react'
import QueryVerifySelect from './verify-select'

export interface QueryWorkspaceProps {
  query: Query
}

const QueryWorkspace: FC<QueryWorkspaceProps> = ({ query }) => {
  const {
    question,
    question_date,
    nl_response,
    user: { name: username },
    sql_query,
    status,
    ai_process,
    last_updated,
  } = query

  const questionDate: Date = new Date(question_date)
  const lastUpdatedDate: Date = new Date(last_updated)
  const [currentSqlQuery, setCurrentSqlQuery] = useState(sql_query)
  const [verifiedStatus, setVerifiedStatus] = useState<QueryStatus>(status)

  const handleSqlChange = (value: string) => {
    setCurrentSqlQuery(value)
  }

  const handleVerifyChange = (verifiedStatus: QueryStatus) => {
    setVerifiedStatus(verifiedStatus)
  }

  return (
    <div className="flex-1 flex flex-col gap-5">
      <div className="flex justify-between gap-3">
        <QueryQuestion {...{ username, question, questionDate }} />
        <div className="flex items-center gap-5 px-6">
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
        className="flex-1 max-h-[50%] flex flex-col gap-5 bg-white border rounded-xl p-6"
      >
        <Tabs defaultValue="sql" className="w-full">
          <TabsList className="w-full">
            <div className="w-full flex gap-3 justify-between">
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
                <Button>
                  <Play className="mr-2" size={20} strokeWidth={2.5} /> Run
                </Button>
              </div>
            </div>
          </TabsList>
          <TabsContent value="sql" className="h-40 pt-3">
            <SqlEditor
              initialQuery={currentSqlQuery}
              onValueChange={handleSqlChange}
            />
          </TabsContent>
          <TabsContent value="process" className="h-40 pt-3 overflow-auto">
            <QueryProcess
              processSteps={
                typeof ai_process === 'string' ? [ai_process] : ai_process
              }
            />
          </TabsContent>
        </Tabs>
        <QueryLastUpdated date={lastUpdatedDate} />
      </div>
      <div className="flex-1">
        <SqlResultsTable
          columns={[]}
          data={[]}
          isLoadingMore={false}
          loadingRef={null}
        />
      </div>
      <div id="nl_response">
        <span className="font-bold">Answer:</span> {nl_response}
        {nl_response}
      </div>
    </div>
  )
}

export default QueryWorkspace
