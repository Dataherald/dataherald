import { LoadingTableRows } from '@/components/queries/loading-rows'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table'
import { Button } from '../ui/button'

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  isLoadingMore: boolean
  isReachingEnd: boolean
  onRowClick: (row: TData) => void
  onLoadMore: () => void
}

export function DataTable<TData, TValue>({
  columns,
  data,
  isLoadingMore = false,
  isReachingEnd = true,
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
      <TableHeader className="bg-gray-50">
        {table.getHeaderGroups().map((headerGroup) => (
          <TableRow key={headerGroup.id}>
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
              className="hover:bg-gray-100 cursor-pointer"
              onClick={() => onRowClick(row.original)}
            >
              {row.getVisibleCells().map((cell) => (
                <TableCell key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </TableCell>
              ))}
            </TableRow>
          ))
        ) : (
          <TableRow className="border-none">
            <TableCell colSpan={columns.length} className="h-24 text-center">
              No results.
            </TableCell>
          </TableRow>
        )}
        {isLoadingMore && <LoadingTableRows columnLength={columns.length} />}
        {!isLoadingMore && (
          <TableRow className="border-none hover:bg-gray-50">
            <TableCell colSpan={columns.length} className="pb-8 text-center">
              {!isReachingEnd ? (
                <Button
                  variant="outline"
                  className="w-full bg-gray-50"
                  onClick={onLoadMore}
                >
                  Load More
                </Button>
              ) : (
                'No previous queries'
              )}
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  )
}
