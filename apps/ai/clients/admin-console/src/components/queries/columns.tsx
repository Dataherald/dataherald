import { CustomColumnDef, SortHeader } from '@/components/data-table'
import {
  formatQueryStatusWithScore,
  getDomainStatus,
  getDomainStatusColors,
} from '@/lib/domain/query'
import { capitalizeFirstLetter, cn, formatKey } from '@/lib/utils'
import { QueryListItem } from '@/models/api'
import { format } from 'date-fns'
import { Check, Minus } from 'lucide-react'

export const getColumns: (config: {
  hiddenColumns: { [id: string]: boolean }
}) => CustomColumnDef<QueryListItem>[] = ({ hiddenColumns }) =>
  (
    [
      {
        id: 'id',
        header: ({ column }) => (
          <div className="min-w-[100px]">
            <SortHeader text="Query ID" column={column} />
          </div>
        ),
        headerFilterDisplay: 'Query ID',
        accessorKey: 'display_id',
      },
      {
        id: 'db_connection_alias',
        header: 'Database',
        headerFilterDisplay: 'Database',
        accessorKey: 'db_connection_alias',
        cell: ({ row }) => (
          <div className="truncate max-w-[10rem] 2xl:max-w-[20rem]">
            {row.getValue('db_connection_alias')}
          </div>
        ),
      },
      {
        id: 'prompt_text',
        header: 'Question',
        headerFilterDisplay: 'Question',
        accessorKey: 'prompt_text',
        cell: ({ row }) => (
          <div className="truncate max-w-[12rem] 2xl:max-w-[25rem]">
            {row.getValue('prompt_text')}
          </div>
        ),
      },
      {
        id: 'sql',
        header: 'Generated SQL',
        headerFilterDisplay: 'Generated SQL',
        accessorKey: 'sql',
        cell: ({ row }) => (
          <div className="truncate max-w-[12rem] 2xl:max-w-[25rem]">
            {row.getValue('sql')}
          </div>
        ),
      },
      {
        id: 'time',
        header: ({ column }) => (
          <div className="min-w-[150px]">
            <SortHeader text="Time" column={column} />
          </div>
        ),
        headerFilterDisplay: 'Time',
        accessorKey: 'created_at',
        cell: ({ row }) =>
          format(new Date(row.getValue('time')), 'yyyy-MM-dd hh:mm a'),
      },
      {
        id: 'created_by',
        header: 'User',
        headerFilterDisplay: 'User',
        accessorKey: 'created_by',
        cell: ({ row }) => (
          <div className="truncate max-w-[10rem] 2xl:max-w-none">
            {row.getValue('created_by')}
          </div>
        ),
      },
      {
        id: 'status',
        header: () => <div className="min-w-[185px]">Status</div>,
        headerFilterDisplay: 'Status',
        accessorFn: ({ status, confidence_score }) => {
          const domainStatus = getDomainStatus(status, confidence_score)
          return formatQueryStatusWithScore(domainStatus, confidence_score)
        },
        cell: ({ row }) => {
          const query = row.original
          const { status, confidence_score } = query
          const textColor = getDomainStatusColors(status, confidence_score).text
          return (
            <div
              className={cn(
                textColor,
                'flex flex-row items-center font-semibold',
              )}
            >
              <div className="w-2 h-2 mr-2 rounded-full bg-current shrink-0" />
              {row.getValue('status')}
            </div>
          )
        },
      },
      {
        id: 'source',
        header: 'Source',
        headerFilterDisplay: 'Source',
        accessorKey: 'source',
        accessorFn: ({ source }) =>
          source ? capitalizeFirstLetter(formatKey(source)) : 'unknown',
      },
      {
        id: 'slack_message_sent',
        header: 'Slack',
        headerFilterDisplay: 'Slack',
        accessorKey: 'slack_message_last_sent_at',
        cell: ({ row }) => (
          <div className="flex items-center justify-center">
            {row.getValue('slack_message_sent') ? (
              <Check className="text-green-700" size={20} strokeWidth={3} />
            ) : (
              <Minus className="text-slate-500 w-3" size={20} strokeWidth={4} />
            )}
          </div>
        ),
      },
    ] as CustomColumnDef<QueryListItem>[]
  ).filter((col) => col.id && !hiddenColumns[col.id])
