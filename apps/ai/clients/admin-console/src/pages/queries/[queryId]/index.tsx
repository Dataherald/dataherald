import QueryLayout from '@/components/query/layout'
import LoadingQuery from '@/components/query/loading'
import { useQuery } from '@/hooks/api/useQuery'
import { Query } from '@/models/api'
import { format } from 'date-fns'
import { Calendar, Clock, User2 } from 'lucide-react'
import { useRouter } from 'next/router'

const QueryPage = () => {
  const router = useRouter()
  const { queryId } = router.query

  const { query, isLoading, isError } = useQuery(Number(queryId))

  if (isLoading)
    return (
      <QueryLayout>
        <LoadingQuery />
      </QueryLayout>
    )

  if (isError) return <div>Error loading the query</div>

  const {
    question,
    user: { name: userName },
    question_date,
  } = query as Query

  const questionDate: Date = new Date(question_date)

  return (
    <QueryLayout>
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
    </QueryLayout>
  )
}

export default QueryPage
