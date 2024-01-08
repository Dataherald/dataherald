import { Skeleton } from '@/components/ui/skeleton'
import { FC } from 'react'

const LoadingUserList: FC = () => (
  <div className="flex flex-col gap-3">
    {[...Array(5)].map((_, index) => (
      <Skeleton className="w-full h-6" key={index} />
    ))}
  </div>
)

export default LoadingUserList
