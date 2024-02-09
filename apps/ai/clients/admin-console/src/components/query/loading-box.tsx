import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import { FC, HTMLAttributes } from 'react'

export type LoadingBoxProps = HTMLAttributes<HTMLDivElement>

const LoadingBox: FC<LoadingBoxProps> = ({ className }) => {
  return (
    <div
      className={cn(
        'w-full h-full bg-slate-50 rounded-lg flex flex-col gap-3',
        className,
      )}
    >
      <Skeleton className="h-full" />
    </div>
  )
}

export default LoadingBox
