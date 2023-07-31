import { Skeleton } from '@/components/ui/skeleton'
import React from 'react'

const LoadingQuery: React.FC = () => {
  return (
    <div className="w-full h-full bg-gray-50 rounded-lg flex flex-col gap-3">
      <div className="flex justify-between gap-5">
        <div className="w-2/3 flex flex-col gap-1">
          <Skeleton className="h-6" />
          <Skeleton className="h-4" />
        </div>
        <Skeleton className="w-1/3 h-11" />
      </div>
      <Skeleton className="h-36" />
      <Skeleton className="h-36" />
      <Skeleton className="h-6 w-2/3" />
    </div>
  )
}

export default LoadingQuery
