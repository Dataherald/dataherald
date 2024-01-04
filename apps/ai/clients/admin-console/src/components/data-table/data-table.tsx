import { LoadingTableRows } from '@/components/data-table/loading-rows'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { cn } from '@/lib/utils'
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table'

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  isLoadingMore?: boolean
  isReachingEnd?: boolean
  noMoreDataMessage?: string
  onRowClick?: (row: TData) => void
  onLoadMore?: () => void
}

export function DataTable<TData, TValue>({
  columns,
  data,
  isLoadingMore = false,
  isReachingEnd = true,
  noMoreDataMessage = '',
  onRowClick,
  onLoadMore,
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <Table>
      <TableHeader>
        {table.getHeaderGroups().map((headerGroup) => (
          <TableRow
            key={headerGroup.id}
            className="bg-gray-50 hover:bg-gray-50"
          >
            {headerGroup.headers.map((header) => {
              return (
                <TableHead key={header.id}>
                  {header.isPlaceholder
                    ? null
                    : flexRender(
                        header.column.columnDef.header,
                        header.getContext(),
                      )}
                </TableHead>
              )
            })}
          </TableRow>
        ))}
      </TableHeader>
      <TableBody>
        {table.getRowModel().rows?.length ? (
          table.getRowModel().rows.map((row) => (
            <TableRow
              key={row.id}
              data-state={row.getIsSelected() && 'selected'}
              className={cn(
                'hover:bg-gray-100 border-b-0 first:border-t-0 border-t',
                onRowClick ? 'cursor-pointer' : '',
              )}
              onClick={() => onRowClick && onRowClick(row.original)}
            >
              {row.getVisibleCells().map((cell) => (
                <TableCell key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </TableCell>
              ))}
            </TableRow>
          ))
        ) : (
          <TableRow className="border-none hover:bg-gray-50">
            <TableCell colSpan={columns.length} className="h-24 text-center">
              No results.
            </TableCell>
          </TableRow>
        )}
        {isLoadingMore && <LoadingTableRows columnLength={columns.length} />}
        {table.getRowModel().rows?.length > 0 && !isLoadingMore && (
          <TableRow className="border-none hover:bg-gray-50">
            <TableCell
              colSpan={columns.length}
              className="p-0 pt-2 text-center"
            >
              {!isReachingEnd ? (
                <Button
                  variant="outline"
                  className="w-full bg-gray-50"
                  onClick={onLoadMore}
                >
                  Load More
                </Button>
              ) : (
                noMoreDataMessage && (
                  <div className="p-4">{noMoreDataMessage}</div>
                )
              )}
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  )
}
