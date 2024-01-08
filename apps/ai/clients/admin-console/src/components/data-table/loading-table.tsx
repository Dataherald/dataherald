import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { cn } from '@/lib/utils'
import { HTMLAttributes } from 'react'

type LoadingTableProps = HTMLAttributes<HTMLDivElement> & {
  columnLength?: number
  rowLength?: number
  disableHeader?: boolean
}

export function LoadingTable({
  columnLength = 5,
  rowLength = 10,
  disableHeader = false,
  className,
}: LoadingTableProps) {
  const columns = Array.from({ length: columnLength })
  return (
    <div className={cn('rounded-md overflow-hidden', className)}>
      <Table>
        {!disableHeader && (
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              {columns.map((_, colIdx) => (
                <TableHead key={colIdx}>
                  <Skeleton className="w-full h-4 bg-slate-400" />
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
        )}
        <TableBody>
          {Array.from({ length: rowLength }).map((_, rowIndex) => (
            <TableRow key={rowIndex} className="hover:bg-transparent">
              {columns.map((_, colIdx) => (
                <TableCell key={colIdx}>
                  <Skeleton className="w-full h-4 bg-slate-300" />
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
