import SqlEditor from '@/components/query/sql-editor'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { formatQueryStatus } from '@/lib/domain/query-status'
import { cn } from '@/lib/utils'
import { EQueryStatus, Query, QueryStatus } from '@/models/api'
import { format } from 'date-fns'
import {
  Calendar,
  CheckCircle,
  Clock,
  Database,
  ListOrdered,
  Play,
  RefreshCw,
  Save,
  User2,
  XCircle,
} from 'lucide-react'
import { FC, useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'

export interface QueryWorkstationProps {
  query: Query
}

const QueryWorkstation: FC<QueryWorkstationProps> = ({ query }) => {
  const {
    question,
    question_date,
    nl_response,
    user: { name: userName },
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

  const verifiedOptionDisplay: JSX.Element = (
    <div className="flex items-center gap-3 capitalize font-semibold text-green-700">
      <CheckCircle strokeWidth={2.5} />
      {formatQueryStatus(EQueryStatus.VERIFIED)}
    </div>
  )
  const notVerifiedOptionDisplay: JSX.Element = (
    <div className="flex items-center gap-3 capitalize font-semibold text-red-500">
      <XCircle strokeWidth={2.5} />
      {formatQueryStatus(EQueryStatus.NOT_VERIFIED)}
    </div>
  )

  return (
    <div className="container p-0 flex-1 flex flex-col gap-5">
      <div className="container p-0 flex justify-between gap-3">
        <div className="container p-0">
          <h1 className="mb-1 font-bold">{question}</h1>
          <h3 className="flex gap-5">
            {[
              { icon: User2, text: userName },
              { icon: Calendar, text: format(questionDate, 'MMMM dd, yyyy') },
              { icon: Clock, text: format(questionDate, 'hh:mm a') },
            ].map((item, index) => (
              <div key={index} className="flex items-center gap-1">
                <item.icon size={16} />
                <span>{item.text}</span>
              </div>
            ))}
          </h3>
        </div>
        <div id="verify" className="min-w-fit flex items-center gap-5 px-8">
          <span className="text-lg">Mark as </span>
          <Select onValueChange={handleVerifyChange}>
            <SelectTrigger
              className={cn(
                'w-[180px]',
                verifiedStatus === EQueryStatus.VERIFIED
                  ? 'border-green-700'
                  : 'border-red-500',
              )}
            >
              {verifiedStatus === EQueryStatus.VERIFIED ? (
                <SelectValue placeholder={verifiedOptionDisplay} />
              ) : (
                <SelectValue placeholder={notVerifiedOptionDisplay} />
              )}
            </SelectTrigger>
            <SelectContent>
              {Object.values(EQueryStatus)
                .filter((qs: QueryStatus) => qs !== EQueryStatus.SQL_ERROR)
                .map((qs: QueryStatus, idx) =>
                  qs === EQueryStatus.VERIFIED ? (
                    <SelectItem
                      key={qs + idx}
                      value={qs}
                      className="focus:bg-green-100"
                    >
                      {verifiedOptionDisplay}
                    </SelectItem>
                  ) : (
                    <SelectItem
                      key={qs + idx}
                      value={qs}
                      className="focus:bg-red-100"
                    >
                      {notVerifiedOptionDisplay}
                    </SelectItem>
                  ),
                )}
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="bg-white border rounded-xl flex-1 flex flex-col gap-5 max-h-[40vh] p-8">
        <Tabs defaultValue="sql" className="w-full h-full">
          <TabsList className="w-full">
            <div className="w-full flex gap-3 justify-between">
              <div id="tabs" className="flex gap-5">
                <TabsTrigger value="sql">
                  <Database className="mr-2" size={20} strokeWidth={2.5} /> SQL
                </TabsTrigger>
                <TabsTrigger value="process">
                  <ListOrdered className="mr-2" size={20} strokeWidth={2.5} />
                  Process
                </TabsTrigger>
              </div>
              <div id="actions" className="flex gap-5">
                <Button variant="outline">
                  <Save className="mr-2" size={20} strokeWidth={2.5} /> Save
                  Edits
                </Button>
                <Button>
                  <Play className="mr-2" size={20} strokeWidth={2.5} /> Run
                </Button>
              </div>
            </div>
          </TabsList>
          <TabsContent value="sql" className="h-48 pt-5">
            <SqlEditor
              initialQuery={currentSqlQuery}
              onValueChange={handleSqlChange}
            />
            <div
              id="last_updated_date"
              className="pt-3 flex flex-row-reverse items-center gap-1 text-gray-400"
            >
              Last updated at {format(lastUpdatedDate, 'yyyy/dd/MM HH:mm a')}
              <RefreshCw size={18} />
            </div>
          </TabsContent>
          <TabsContent value="process" className="h-48 pt-5 overflow-auto">
            <ol>
              {(typeof ai_process === 'string' ? [ai_process] : ai_process).map(
                (step, idx) => (
                  <li key={idx} className="mb-2 last:mb-0">
                    <div className="flex gap-2">
                      <span className="text-primary font-bold">
                        {idx + 1}.{' '}
                      </span>
                      {step}
                    </div>
                  </li>
                ),
              )}
            </ol>
          </TabsContent>
        </Tabs>
      </div>
      <div id="nl_response">
        <span className="font-bold">Answer:</span> {nl_response}
      </div>
    </div>
  )
}

export default QueryWorkstation
