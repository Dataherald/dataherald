import { format } from 'date-fns'
import { Calendar, Clock, User2 } from 'lucide-react'
import { FC } from 'react'

export interface QueryQuestionProps {
  username: string
  question: string
  questionDate: Date
}

const QueryQuestion: FC<QueryQuestionProps> = ({
  username,
  question,
  questionDate,
}) => (
  <div>
    <h1 className="mb-1 font-bold">{question}</h1>
    <h3 className="flex gap-5">
      {[
        { icon: User2, text: username },
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
)

export default QueryQuestion
