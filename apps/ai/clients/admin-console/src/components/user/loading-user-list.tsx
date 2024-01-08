import { Skeleton } from '@/components/ui/skeleton'
import { FC } from 'react'

const LoadingUserList: FC = () => (
  <div className="flex flex-col gap-3">
    {[...Array(5)].map((_, index) => (
      <div className="h-5 flex justify-between" key={index}>
        <Skeleton className="w-10/12 h-full" />
        <Skeleton className="w-8 h-full" />
      </div>
    ))}
  </div>
)

export default LoadingUserList
