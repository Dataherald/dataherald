import {
  formatQueryStatus,
  getDomainStatus,
  getDomainStatusColor,
} from '@/lib/domain/query-status'
import { cn } from '@/lib/utils'
import { Query } from '@/models/api'
import { EDomainQueryStatus } from '@/models/domain'
import { ColumnDef } from '@tanstack/react-table'
import { Microscope } from 'lucide-react'

export const columns: ColumnDef<Query>[] = [
  {
    id: 'status-icon',
    header: '',
    cell: ({ row }) => {
      const query = row.original
      const { status, evaluation } = query
      const textColor = getDomainStatusColor(status, evaluation)
      return (
        <div className="relative flex items-center justify-center w-8 h-8 rounded-full border border-gray-400">
          <Microscope size={18} />
          <div
            className={cn(
              textColor,
              'w-2 h-2 rounded-full bg-current flex-shrink-0',
              'absolute bottom-0 right-0',
            )}
          />
        </div>
      )
    },
  },
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
      return `${formatQueryStatus(domainStatus)} ${
        status !== EDomainQueryStatus.SQL_ERROR
          ? `(${evaluation.confidence_level}%)`
          : ''
      }`
    },
    cell: ({ row }) => {
      const query = row.original
      const { status, evaluation } = query
      const textColor = getDomainStatusColor(status, evaluation)
      return (
        <div className={cn(textColor, 'flex flex-row items-center capitalize')}>
          <div className="w-2 h-2 mr-2 rounded-full bg-current flex-shrink-0" />
          {row.getValue('status_col')}
        </div>
      )
    },
  },
]
