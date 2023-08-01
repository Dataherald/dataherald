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
  Save,
  User2,
} from 'lucide-react'
import { FC, useState } from 'react'

export interface QueryWorkstationProps {
  query: Query
}

const QueryWorkstation: FC<QueryWorkstationProps> = ({ query }) => {
  const {
    question,
    nl_response,
    user: { name: userName },
    question_date,
    sql_query,
  } = query

  const questionDate: Date = new Date(question_date)
  const [currentSqlQuery, setCurrentSqlQuery] = useState(sql_query)

  const handleSqlChange = (value: string) => {
    setCurrentSqlQuery(value)
    console.log(currentSqlQuery)
  }
  return (
    <div className="container p-0 flex-1 flex flex-col gap-5">
      <div className="container p-0">
        <h1 className="m-0 font-bold capitalize">{question}</h1>
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
      <div className="bg-white border rounded-xl flex-1 flex flex-col gap-5 max-h-[40vh] py-8">
        <div className="flex gap-3 justify-between">
          <div id="tabs" className="flex gap-5 px-8">
            <Button variant="outline">
              <Database className="mr-2" size={16} /> SQL
            </Button>
            <Button variant="outline">
              <ListOrdered className="mr-2" size={16} /> Process
            </Button>
          </div>
          <div id="actions" className="flex gap-3 px-8">
            <Button variant="outline">
              <Save className="mr-2" size={16} /> Save Edits
            </Button>
            <Button>
              <Play className="mr-2" size={16} /> Run
            </Button>
          </div>
        </div>
        <div id="sql-editor" className="flex-1">
          <SqlEditor initialQuery={sql_query} onValueChange={handleSqlChange} />
        </div>
      </div>
      <div id="nl_response">
        <span className="font-bold">Answer:</span> {nl_response}
      </div>
    </div>
  )
}

export default QueryWorkstation
