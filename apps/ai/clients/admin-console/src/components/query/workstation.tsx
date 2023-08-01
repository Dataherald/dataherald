import SqlEditor from '@/components/query/sql-editor'
import { Button } from '@/components/ui/button'
import { Query } from '@/models/api'
import { format } from 'date-fns'
import {
  Calendar,
  Clock,
  Database,
  ListOrdered,
  Play,
  RefreshCw,
  Save,
  User2,
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
    ai_process,
    last_updated,
  } = query

  const questionDate: Date = new Date(question_date)
  const lastUpdatedDate: Date = new Date(last_updated)
  const [currentSqlQuery, setCurrentSqlQuery] = useState(sql_query)

  const handleSqlChange = (value: string) => {
    setCurrentSqlQuery(value)
  }

  return (
    <div className="container p-0 flex-1 flex flex-col gap-5">
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
          <TabsContent value="process" className="h-48 pt-5">
            {ai_process}
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
