import {
  formatQueryStatus,
  getDomainStatus,
  getDomainStatusColor,
} from '@/lib/domain/query-status'
import { cn } from '@/lib/utils'
import { Query } from '@/models/api'
import { ColumnDef } from '@tanstack/react-table'

export const columns: ColumnDef<Query>[] = [
  {
    header: () => <div className="min-w-[60px]">Query ID</div>,
    accessorKey: 'id',
  },
  {
    header: 'User',
    accessorKey: 'user.name',
  },
  {
    header: 'Question',
    accessorKey: 'question',
  },
  {
    header: 'Answer',
    accessorKey: 'nl_response',
  },
  {
    id: 'time_col',
    header: () => <div className="lg:min-w-[150px]">Time</div>,
    accessorKey: 'question_date',
  },
  {
    id: 'status_col',
    header: () => <div className="xl:min-w-[200px]">Status</div>,
    accessorFn: ({ status, evaluation }) => {
      const domainStatus = getDomainStatus(status, evaluation)
      return `${formatQueryStatus(domainStatus)} (${
        evaluation.confidence_level
      }%)`
    },
    cell: ({ row }) => {
      const query = row.original
      const { status, evaluation } = query
      const textColor = `text-${getDomainStatusColor(status, evaluation)}`
      return (
        <div className={cn(textColor, 'flex flex-row items-center capitalize')}>
          <div className="w-2 h-2 mr-2 rounded-full bg-current flex-shrink-0" />
          {row.getValue('status_col')}
        </div>
      )
    },
  },
]
