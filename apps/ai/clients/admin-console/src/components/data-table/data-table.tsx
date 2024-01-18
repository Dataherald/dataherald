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
  Column,
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table'
import { ArrowDown, ArrowUp, RefreshCcw } from 'lucide-react'
import { useState } from 'react'

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  isRefreshing?: boolean
  isLoadingMore?: boolean
  isReachingEnd?: boolean
  noMoreDataMessage?: string
  enableFiltering?: boolean
  onRowClick?: (row: TData) => void
  onLoadMore?: () => void
  onRefresh?: () => void
}

export function DataTable<TData, TValue>({
  columns,
  data,
  isRefreshing = false,
  isLoadingMore = false,
  isReachingEnd = true,
  noMoreDataMessage = '',
  enableFiltering = false,
  onRowClick,
  onLoadMore,
  onRefresh,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
    },
  })

  return (
    <div className="flex flex-col">
      {onRefresh && (
        <div
          className={cn(
            'flex items-center',
            enableFiltering ? 'justify-between' : 'justify-end',
          )}
        >
          {enableFiltering && <>{/* TODO */}</>}
          <Button
            variant="ghost"
            disabled={isRefreshing || isLoadingMore}
            onClick={onRefresh}
          >
            <RefreshCcw
              size={18}
              className={isRefreshing || isLoadingMore ? 'animate-spin' : ''}
            />
          </Button>
        </div>
      )}
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
                  <TableCell
                    key={cell.id}
                    style={{ width: `${cell.column.getSize()}px` || 'auto' }}
                  >
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
    </div>
  )
}

interface SortHeaderProps<T> {
  text: string
  column: Column<T, unknown>
}

export const SortHeader = <T,>({ text, column }: SortHeaderProps<T>) => (
  <Button
    variant="ghost"
    className="p-0 hover:bg-transparent uppercase"
    onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
  >
    {text}
    {column.getIsSorted() === 'asc' ? (
      <ArrowUp className="ml-2 h-4 w-4" />
    ) : (
      <ArrowDown className="ml-2 h-4 w-4" />
    )}
  </Button>
)
