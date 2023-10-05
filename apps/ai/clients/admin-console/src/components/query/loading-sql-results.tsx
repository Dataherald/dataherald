import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import { FC, HTMLAttributes } from 'react'

export type LoadingSqlQueryResultsProps = HTMLAttributes<HTMLDivElement>

const LoadingSqlQueryResults: FC<LoadingSqlQueryResultsProps> = ({
  className,
}) => {
  return (
    <div
      className={cn(
        'w-full h-full bg-gray-50 rounded-lg flex flex-col gap-3',
        className,
      )}
    >
      <Skeleton className="h-full" />
    </div>
  )
}

export default LoadingSqlQueryResults
