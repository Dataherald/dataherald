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
import { Badge, badgeVariants } from '@/components/ui/badge'
import { formatKey } from '@/lib/utils'
import { EGoldenSqlSource, GoldenSqlListItem } from '@/models/api'
import { format } from 'date-fns'
import { ExternalLink, Trash2 } from 'lucide-react'
import Link from 'next/link'

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
      <div className="min-w-[140px]">
        <SortHeader text="Time added" column={column} />
      </div>
    ),
    headerFilterDisplay: 'Time added',
    accessorKey: 'created_at',
    cell: ({ row }) =>
      format(new Date(row.getValue('created_at')), 'yyyy-MM-dd hh:mm a'),
  },
  {
    id: 'source',
    header: 'Source',
    headerFilterDisplay: 'Source',
    accessorFn: ({
      metadata: {
        dh_internal: { source },
      },
    }) => formatKey(source),
    cell: ({ row }) => {
      const { source, prompt_id } = row.original.metadata.dh_internal
      const badge =
        source === EGoldenSqlSource.VERIFIED_QUERY ? (
          <Link
            className={badgeVariants({ variant: 'success' })}
            href={`/queries/${prompt_id as string}`}
          >
            <span className="mr-1">{row.getValue('source')}</span>
            <div>
              <ExternalLink size={14} strokeWidth={2.5} />
            </div>
          </Link>
        ) : (
          <Badge variant="sky">{row.getValue('source')}</Badge>
        )
      return <div className="capitalize">{badge}</div>
    },
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
          <AlertDialogTrigger className="rounded-xl p-2 hover:bg-gray-200 hover:text-black/90">
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
