import { formatStatus } from '@/lib/utils'
import { FineTuningModel } from '@/models/api'
import { ColumnDef } from '@tanstack/react-table'
import { format } from 'date-fns'

export const finetunningsColumns: ColumnDef<FineTuningModel>[] = [
  {
    id: 'alias',
    header: 'Name',
    cell: ({ row }) => {
      const { id, alias } = row.original
      return <div>{alias || id}</div>
    },
  },
  {
    id: 'db_connection_alias',
    header: 'Database',
    accessorKey: 'db_connection_alias',
  },
  {
    id: 'model_name',
    header: 'Model',
    accessorKey: 'base_llm.model_name',
  },
  {
    id: 'created_at',
    header: () => <div className="min-w-[6rem]">Created at</div>,
    accessorKey: 'created_at',
    cell: ({ row }) => {
      const date: string = row.getValue('created_at')
      return date ? format(new Date(date), 'PP') : '-'
    },
  },
  {
    id: 'status',
    header: 'Status',
    accessorKey: 'status',
    cell: ({ row }) => formatStatus(row.getValue('status')),
  },
]
