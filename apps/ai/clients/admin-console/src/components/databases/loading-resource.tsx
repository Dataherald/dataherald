import { Skeleton } from '@/components/ui/skeleton'
import { FC } from 'react'

const LoadingDatabaseResource: FC = () => (
  <div>
    <div className="flex flex-col gap-4">
      <Skeleton className="w-4/5 h-12"></Skeleton>
      <Skeleton className="w-full h-32"></Skeleton>
      <Skeleton className="w-full h-48"></Skeleton>
    </div>
  </div>
)

export default LoadingDatabaseResource
