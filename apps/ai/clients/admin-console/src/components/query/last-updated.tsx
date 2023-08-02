import { format } from 'date-fns'
import { RefreshCw } from 'lucide-react'
import { FC } from 'react'

export interface LastUpdatedProps {
  date: Date
}

const QueryLastUpdated: FC<LastUpdatedProps> = ({ date }) => (
  <div
    id="last_updated_date"
    className="flex flex-row-reverse items-center gap-1 text-gray-400 text-sm"
  >
    Last updated at {format(date, 'yyyy/dd/MM HH:mm a')}
    <RefreshCw size={14} />
  </div>
)

export default QueryLastUpdated
