import {
  formatQueryStatus,
  getDomainStatus,
  getDomainStatusColor,
} from '@/lib/domain/query-status'
import { cn } from '@/lib/utils'
import { QueryListItem } from '@/models/api'
import { EDomainQueryStatus } from '@/models/domain'
import { ColumnDef } from '@tanstack/react-table'
import { format } from 'date-fns'

export const columns: ColumnDef<QueryListItem>[] = [
  {
    id: 'id',
    header: 'Query ID',
    accessorKey: 'id',
    cell: ({ row }) => (
      <div className="truncate max-w-[5rem] 2xl:max-w-none">
        {row.getValue('id')}
      </div>
    ),
  },
  {
    id: 'username',
    header: 'User',
    accessorKey: 'username',
    cell: ({ row }) => (
      <div className="truncate max-w-[10rem] 2xl:max-w-none">
        {row.getValue('username')}
      </div>
    ),
  },
  {
    id: 'question',
    header: 'Question',
    accessorKey: 'question',
    cell: ({ row }) => (
      <div className="truncate max-w-[12rem] 2xl:max-w-[25rem]">
        {row.getValue('question')}
      </div>
    ),
  },
  {
    id: 'answer',
    header: 'Answer',
    accessorKey: 'nl_response',
    cell: ({ row }) => (
      <div className="truncate max-w-[12rem] 2xl:max-w-[25rem]">
        {row.getValue('answer')}
      </div>
    ),
  },
  {
    id: 'time',
    header: () => <div className="min-w-[140px]">Time</div>,
    accessorKey: 'question_date',
    cell: ({ row }) =>
      format(new Date(row.getValue('time')), 'yyyy-MM-dd hh:mm a'),
  },
  {
    id: 'status',
    header: () => <div className="min-w-[185px]">Status</div>,
    accessorFn: ({ status, evaluation_score }) => {
      const domainStatus = getDomainStatus(status, evaluation_score)
      return `${formatQueryStatus(domainStatus)} ${
        status !== EDomainQueryStatus.SQL_ERROR ? `(${evaluation_score}%)` : ''
      }`
    },
    cell: ({ row }) => {
      const query = row.original
      const { status, evaluation_score } = query
      const textColor = getDomainStatusColor(status, evaluation_score)
      return (
        <div
          className={cn(
            textColor,
            'flex flex-row items-center capitalize font-semibold',
          )}
        >
          <div className="w-2 h-2 mr-2 rounded-full bg-current shrink-0" />
          {row.getValue('status')}
        </div>
      )
    },
  },
]
