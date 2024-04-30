import { LoadingTableRows } from '@/components/data-table/loading-rows'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import SearchInput from '@/components/ui/search-input'
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
import { ReactNode, useEffect, useState } from 'react'

export type CustomColumnDef<
  TData extends RowData,
  TValue = unknown,
> = ColumnDef<TData, TValue> & {
  headerFilterDisplay?: string
}

interface DataTableProps<TData, TValue> {
  id: string
  columns: CustomColumnDef<TData, TValue>[] | CustomColumnDef<TData, TValue>[]
  data: TData[]
  isLoadingFirst?: boolean
  isRefreshing?: boolean
  isLoadingMore?: boolean
  isReachingEnd?: boolean
  noMoreDataMessage?: string
  enableColumnVisibility?: boolean
  searchText?: string
  onSearchTextChange?: (search: string) => void
  onSearchTextClear?: () => void
  searchInfo?: ReactNode
  onRowClick?: (row: TData) => void
  onLoadMore?: () => void
  onRefresh?: () => void
}

export function DataTable<TData, TValue>({
  id,
  columns,
  data,
  isLoadingFirst = false,
  isRefreshing = false,
  isLoadingMore = false,
  isReachingEnd = true,
  noMoreDataMessage = '',
  enableColumnVisibility = false,
  searchText = '',
  searchInfo = null,
  onSearchTextChange,
  onSearchTextClear,
  onRowClick,
  onLoadMore,
  onRefresh,
}: DataTableProps<TData, TValue>) {
  const LOCAL_STORAGE_KEY = `data-table-${id}`
  const tableConfig = localStorage.getItem(LOCAL_STORAGE_KEY)
  const [sorting, setSorting] = useState<SortingState>(() => {
    return tableConfig ? JSON.parse(tableConfig).sorting : []
  })
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>(
    () => {
      const defaultVisibility = Object.fromEntries(
        columns
          .filter((c) => c.enableHiding !== false)
          .map(({ id }) => [id, true]),
      )
      return tableConfig
        ? JSON.parse(tableConfig).columnVisibility
        : defaultVisibility
    },
  )

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onColumnVisibilityChange: setColumnVisibility,
    state: {
      sorting,
      columnVisibility,
    },
  })

  const isSearchEnabled =
    onSearchTextChange !== undefined && onSearchTextClear !== undefined

  useEffect(() => {
    const stateToSave = { sorting, columnVisibility }
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(stateToSave))
  }, [sorting, columnVisibility, LOCAL_STORAGE_KEY])

  return (
    <div className="flex flex-col gap-1">
      {onRefresh && (
        <div
          className={cn(
            'flex items-center',
            isSearchEnabled ? 'justify-between' : 'justify-end',
          )}
        >
          {isSearchEnabled && (
            <div className="w-full flex items-center gap-3 max-w-sm">
              <SearchInput
                placeholder="Search..."
                className="h-fit"
                value={searchText}
                onChange={(e) => onSearchTextChange(e.target.value)}
                onClear={onSearchTextClear}
                onKeyUp={(e) => {
                  if (e.key === 'Enter') {
                    onSearchTextChange(e.currentTarget.value)
                  }
                }}
              />
              {searchInfo}
            </div>
          )}
          <div className="flex items-center gap-2">
            {enableColumnVisibility && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="outline"
                    className="border-input hover:bg-white text-sm"
                  >
                    <Columns3 size={14} className="mr-2" />
                    Select visible columns
                    <ChevronDown size={16} className="ml-2" />
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
                            value === true || // always let display the column
                            (value === false && // check if there are more than 1 visible columns before hiding
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
              size="icon"
              disabled={isRefreshing || isLoadingMore}
              onClick={onRefresh}
            >
              <RefreshCcw
                size={16}
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
              className="bg-slate-50 hover:bg-slate-50"
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
          {isLoadingFirst ? (
            <LoadingTableRows
              rowLength={10}
              columnLength={
                Object.values(columnVisibility).filter((v) => !!v).length
              }
            />
          ) : table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                data-state={row.getIsSelected() && 'selected'}
                className={cn(
                  'hover:bg-slate-100 border-b-0 first:border-t-0 border-t',
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
            <TableRow className="border-none hover:bg-slate-50">
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
          {table.getRowModel().rows?.length > 0 && !isLoadingMore && (
            <TableRow className="border-none hover:bg-slate-50">
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
      variant="icon"
      className="uppercase"
      onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
    >
      {text}
      <OrderIcon className="ml-2 h-4 w-4" />
    </Button>
  )
}
