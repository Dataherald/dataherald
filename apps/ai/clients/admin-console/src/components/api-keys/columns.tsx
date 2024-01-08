import DeleteApiKeyDialog from '@/components/api-keys/delete-api-key-dialog'
import { ApiKey } from '@/models/api'
import { ColumnDef } from '@tanstack/react-table'
import { format } from 'date-fns'

export const getApiKeysColumns: (actions: {
  remove: (id: string) => void | Promise<void>
}) => ColumnDef<ApiKey>[] = ({ remove }) => [
  {
    id: 'name',
    header: 'Name',
    accessorKey: 'name',
  },
  {
    id: 'key_preview',
    header: 'Secret key',
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
  {
    id: 'delete',
    width: 'auto',
    size: 20,
    cell: ({ row }) => {
      const { id } = row.original
      return <DeleteApiKeyDialog deleteFnc={() => remove(id)} />
    },
  },
]
