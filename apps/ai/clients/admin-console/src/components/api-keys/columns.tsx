import { ApiKey } from '@/models/api'
import { ColumnDef } from '@tanstack/react-table'
import { format } from 'date-fns'

export const apiKeysColumns: ColumnDef<ApiKey>[] = [
  {
    id: 'name',
    header: 'Name',
    accessorKey: 'name',
  },
  {
    id: 'key_preview',
    header: 'Key',
    accessorKey: 'key_preview',
  },
  {
    id: 'created_at',
    header: () => <div className="min-w-[5rem]">Created at</div>,
    accessorKey: 'created_at',
    cell: ({ row }) => {
      const date: string = row.getValue('created_at')
      return date ? format(new Date(date), 'PP') : '-'
    },
  },
]
