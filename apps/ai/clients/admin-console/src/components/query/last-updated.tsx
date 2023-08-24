import { format } from 'date-fns'
import { RefreshCw } from 'lucide-react'
import { FC } from 'react'

export interface LastUpdatedProps {
  responsible?: string
  date: Date
}

const QueryLastUpdated: FC<LastUpdatedProps> = ({ responsible, date }) => (
  <div
    id="last_updated_date"
    className="flex flex-row-reverse items-center gap-1 text-gray-400 text-sm"
  >
    Last updated at {format(date, 'yyyy/dd/MM HH:mm a')}{' '}
    {responsible && `by ${(<span className="capitalize">{responsible}</span>)}`}
    <RefreshCw size={14} />
  </div>
)

export default QueryLastUpdated
