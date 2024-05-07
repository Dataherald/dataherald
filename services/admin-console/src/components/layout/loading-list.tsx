import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import { FC, HTMLAttributes } from 'react'

export interface LoadingListProps {
  length?: number
  height?: number
}

const LoadingList: FC<LoadingListProps & HTMLAttributes<HTMLDivElement>> = ({
  length = 5,
  height,
  className,
}) => {
  const skeletonHeight = height ? `h-${height}` : 'h-8'
  return (
    <div className={cn('flex flex-col gap-3', className)}>
      {[...Array(length)].map((_, index) => (
        <Skeleton className={cn('w-full', skeletonHeight)} key={index} />
      ))}
    </div>
  )
}

export default LoadingList
