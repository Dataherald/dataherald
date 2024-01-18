import { LoadingTableRows } from '@/components/data-table/loading-rows'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
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
  RowData,
  SortingState,
  VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table'
import {
  ArrowDown,
  ArrowDownUp,
  ArrowUp,
  ChevronDown,
  Columns3,
  LucideIcon,
  RefreshCcw,
} from 'lucide-react'
import { useState } from 'react'

export type CustomColumnDef<
  TData extends RowData,
  TValue = unknown,
> = ColumnDef<TData, TValue> & {
  headerFilterDisplay?: string
}

interface DataTableProps<TData, TValue> {
  columns: CustomColumnDef<TData, TValue>[] | CustomColumnDef<TData, TValue>[]
  data: TData[]
  isRefreshing?: boolean
  isLoadingMore?: boolean
  isReachingEnd?: boolean
  noMoreDataMessage?: string
  enableFiltering?: boolean
  enableColumnVisibility?: boolean
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
  enableColumnVisibility = false,
  onRowClick,
  onLoadMore,
  onRefresh,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [globalFilter, setGlobalFilter] = useState('')
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>(
    Object.fromEntries(columns.map(({ id }) => [id, true])),
  )

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    onColumnVisibilityChange: setColumnVisibility,
    state: {
      sorting,
      globalFilter,
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
          {enableFiltering && (
            <div className="w-full flex items-center max-w-sm py-3">
              <Input
                placeholder="Search..."
                value={globalFilter}
                onChange={(e) => setGlobalFilter(e.target.value)}
              />
            </div>
          )}
          <div className="flex items-center gap-2">
            {enableColumnVisibility && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="ml-auto text-slate-500">
                    <Columns3 size={18} className="mr-2" />
                    Select visible columns
                    <ChevronDown size={18} className="ml-2" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {table
                    .getAllColumns()
                    .filter((column) => column.getCanHide())
                    .map((column) => {
                      return (
                        <DropdownMenuCheckboxItem
                          key={column.id}
                          className="capitalize pe-10 cursor-pointer max-w-lg"
                          checked={column.getIsVisible()}
                          onCheckedChange={(value) =>
                            value === true ||
                            (value === false &&
                              Object.values(columnVisibility).filter(
                                (v) => v === true,
                              ).length > 1)
                              ? column.toggleVisibility(!!value)
                              : undefined
                          }
                        >
                          {
                            (column.columnDef as CustomColumnDef<TData, TValue>)
                              .headerFilterDisplay
                          }
                        </DropdownMenuCheckboxItem>
                      )
                    })}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
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
          {isLoadingMore && (
            <LoadingTableRows
              columnLength={
                Object.values(columnVisibility).filter((v) => v !== false)
                  .length || columns.length
              }
            />
          )}
          {!globalFilter &&
            table.getRowModel().rows?.length > 0 &&
            !isLoadingMore && (
              <TableRow className="border-none hover:bg-gray-50">
                <TableCell
                  colSpan={columns.length}
                  className="p-0 pt-2 text-center"
                >
                  {!isReachingEnd ? (
                    <Button
                      variant="outline"
                      className="w-full bg-slate-50 text-slate-900 hover:bg-slate-100 border-slate-300"
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

export const SortHeader = <T,>({ text, column }: SortHeaderProps<T>) => {
  const OrderIcon: LucideIcon =
    column.getIsSorted() === false
      ? ArrowDownUp
      : column.getIsSorted() === 'asc'
      ? ArrowUp
      : ArrowDown
  return (
    <Button
      variant="ghost"
      className="p-0 hover:bg-transparent uppercase"
      onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
    >
      {text}
      <OrderIcon className="ml-2 h-4 w-4" />
    </Button>
  )
}
