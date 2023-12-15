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
import { ColumnDef } from '@tanstack/react-table'
import { format } from 'date-fns'
import { ExternalLink, Trash2 } from 'lucide-react'
import Link from 'next/link'

export const getColumns: (actions: {
  deleteAction: (id: string) => void
}) => ColumnDef<GoldenSqlListItem>[] = ({ deleteAction }) => [
  {
    id: 'id',
    header: () => <div className="min-w-[70px]">ID</div>,
    accessorKey: 'display_id',
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
    id: 'sql_query',
    header: 'SQL Query',
    accessorKey: 'sql_query',
    cell: ({ row }) => (
      <div className="truncate max-w-[12rem] 2xl:max-w-[25rem]">
        {row.getValue('sql_query')}
      </div>
    ),
  },
  {
    id: 'created_time',
    header: () => <div className="min-w-[140px]">Time added</div>,
    accessorKey: 'created_time',
    cell: ({ row }) =>
      format(new Date(row.getValue('created_time')), 'yyyy-MM-dd hh:mm a'),
  },
  {
    id: 'source',
    header: 'Source',
    accessorKey: 'source',
    cell: ({ row }) => {
      const { source, verified_query_id } = row.original
      const badge =
        source === EGoldenSqlSource.VERIFIED_QUERY ? (
          <Link
            className={badgeVariants({ variant: 'success' })}
            href={`/queries/${verified_query_id as string}`}
          >
            <span className="mr-1">{formatKey(row.getValue('source'))}</span>
            <ExternalLink size={14} strokeWidth={2.5} />
          </Link>
        ) : (
          <Badge variant="sky">{formatKey(row.getValue('source'))}</Badge>
        )
      return <div className="capitalize">{badge}</div>
    },
  },
  {
    id: 'delete',
    cell: ({ row }) => {
      const { id, source } = row.original
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
            <Trash2 strokeWidth={1.5} />
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
