import { cn } from '@/lib/utils'
import { EQueryStatus, Query } from '@/models/api'
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
    accessorFn: ({ status, evaluation: { confidence_level } }) => {
      switch (status) {
        case EQueryStatus.SQL_ERROR:
          return 'SQL Error'
        case EQueryStatus.NOT_VERIFIED: {
          let text = ''

          if (confidence_level < 70) {
            text = 'Low confidence'
          } else if (confidence_level < 90) {
            text = 'Medium confidence'
          } else {
            text = 'High confidence'
          }

          return `${text} (${confidence_level}%)`
        }
        case EQueryStatus.VERIFIED:
          return 'Verified (100%)'
      }
    },
    cell: ({ row }) => {
      const query = row.original
      let textColor = ''
      const {
        status,
        evaluation: { confidence_level },
      } = query
      switch (status) {
        case EQueryStatus.SQL_ERROR:
          textColor = 'text-red-500'
          break
        case EQueryStatus.NOT_VERIFIED:
          {
            if (confidence_level < 70) {
              textColor = 'text-orange-600'
            } else if (confidence_level < 90) {
              textColor = 'text-yellow-500'
            } else {
              textColor = 'text-green-500'
            }
          }
          break
        case EQueryStatus.VERIFIED:
          textColor = 'text-green-700'
          break
      }
      return (
        <div className={cn(textColor, 'flex flex-row items-center')}>
          <div className="w-2 h-2 mr-2 rounded-full bg-current flex-shrink-0" />
          {row.getValue('status_col')}
        </div>
      )
    },
  },
]
