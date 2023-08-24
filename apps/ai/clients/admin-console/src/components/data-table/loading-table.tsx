import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface LoadingTableProps {
  columnLength?: number
  rowLength?: number
  disableHeader?: boolean
}

export function LoadingTable({
  columnLength = 5,
  rowLength = 10,
  disableHeader = false,
}: LoadingTableProps) {
  const columns = Array.from({ length: columnLength })
  return (
    <div className="rounded-md overflow-hidden">
      <Table>
        {!disableHeader && (
          <TableHeader className="bg-gray-400">
            <TableRow className="hover:bg-transparent">
              {columns.map((_, colIdx) => (
                <TableHead key={colIdx}>
                  <Skeleton className="w-full h-4" />
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
                  <Skeleton className="w-full h-4" />
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
