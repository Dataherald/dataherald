import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import { FC, HTMLAttributes } from 'react'

export type LoadingQueryResultsProps = HTMLAttributes<HTMLDivElement>

const LoadingQueryResults: FC<LoadingQueryResultsProps> = ({ className }) => {
  return (
    <div
      className={cn(
        'w-full h-full bg-gray-50 rounded-lg flex flex-col gap-3',
        className,
      )}
    >
      <Skeleton className="h-4/5" />
      <Skeleton className="h-1/5 w-2/3" />
    </div>
  )
}

export default LoadingQueryResults
