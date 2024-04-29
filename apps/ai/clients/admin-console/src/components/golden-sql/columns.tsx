import { CustomColumnDef, SortHeader } from '@/components/data-table'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { EGoldenSqlSource, GoldenSqlListItem } from '@/models/api'
import { format } from 'date-fns'
import { Trash2 } from 'lucide-react'

export const getColumns: (actions: {
  deleteAction: (id: string) => void
}) => CustomColumnDef<GoldenSqlListItem>[] = ({ deleteAction }) => [
  {
    id: 'id',
    header: ({ column }) => {
      return (
        <div className="min-w-[70px]">
          <SortHeader text="ID" column={column} />
        </div>
      )
    },
    headerFilterDisplay: 'ID',
    accessorKey: 'metadata.dh_internal.display_id',
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
    header: 'SQL',
    headerFilterDisplay: 'SQL',
    accessorKey: 'sql',
    cell: ({ row }) => (
      <div className="truncate max-w-[12rem] 2xl:max-w-[25rem]">
        {row.getValue('sql')}
      </div>
    ),
  },
  {
    id: 'created_at',
    header: ({ column }) => (
      <div className="min-w-[150px]">
        <SortHeader text="Time added" column={column} />
      </div>
    ),
    headerFilterDisplay: 'Time added',
    accessorKey: 'created_at',
    cell: ({ row }) =>
      format(new Date(row.getValue('created_at')), 'yyyy-MM-dd hh:mm a'),
  },
  {
    id: 'delete',
    size: 20,
    enableHiding: false,
    cell: ({ row }) => {
      const { id } = row.original
      const { source } = row.original.metadata.dh_internal
      const handleDeleteConfirm = () => deleteAction(id)
      const deleteText: JSX.Element =
        source === EGoldenSqlSource.VERIFIED_QUERY ? (
          <>
            This will remove the query from Golden SQL list used for AI training
            and not include it in future models. Also, the source query will be
            marked as <strong>Not Verified</strong> in the editor.
          </>
        ) : (
          <>
            This will remove the query from Golden SQL list used for AI training
            and not include it in future models. You will need to upload this
            query again to be used for training.
          </>
        )
      return (
        <AlertDialog>
          <AlertDialogTrigger className="rounded-xl p-2 hover:bg-slate-200 hover:text-black/90">
            <Trash2 strokeWidth={1.5} size={20} />
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Remove from Golden SQL list?</AlertDialogTitle>
              <AlertDialogDescription>{deleteText}</AlertDialogDescription>
              <AlertDialogDescription>
                Do you wish to continue?
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                variant="destructive"
                onClick={handleDeleteConfirm}
              >
                Confirm Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      )
    },
  },
]
