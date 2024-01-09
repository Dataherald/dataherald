import { Skeleton } from '@/components/ui/skeleton'
import { FC } from 'react'

interface LoadingQueryProps {
  enableHeader?: boolean
}

const LoadingQuery: FC<LoadingQueryProps> = ({ enableHeader = true }) => {
  return (
    <div className="w-full h-full flex flex-col">
      {enableHeader && (
        <div className="flex justify-between gap-32 px-6 pt-5 pb-3">
          <div className="w-2/3 flex flex-col gap-2">
            <Skeleton className="h-10" />
            <Skeleton className="h-8" />
          </div>
          <div className="w-1/3 flex flex-col gap-2">
            <Skeleton className="h-10" />
            <Skeleton className="h-8" />
          </div>
        </div>
      )}
      <Skeleton className="h-1/2 mx-6 my-3" />
      <Skeleton className="h-1/2 mx-6 my-3" />
    </div>
  )
}

export default LoadingQuery
