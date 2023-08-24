import { Skeleton } from '@/components/ui/skeleton'
import { TableCell, TableRow } from '@/components/ui/table'

interface LoadingTableRowsProps {
  columnLength?: number
  rowLength?: number
}

export function LoadingTableRows({
  columnLength = 5,
  rowLength = 3,
}: LoadingTableRowsProps) {
  const rows = Array.from({ length: rowLength })
  const columns = Array.from({ length: columnLength })
  return (
    <>
      {rows.map((_, rowIndex) => (
        <TableRow key={rowIndex} className="hover:bg-transparent">
          {columns.map((_, colIdx) => (
            <TableCell key={colIdx}>
              <Skeleton className="w-full h-4" />
            </TableCell>
          ))}
        </TableRow>
      ))}
    </>
  )
}
