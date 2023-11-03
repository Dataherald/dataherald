import { SectionHeader } from '@/components/query/section-header'
import { Skeleton } from '@/components/ui/skeleton'
import { FC } from 'react'

const LoadingQuery: FC = () => {
  return (
    <div className="w-full h-full flex flex-col gap-3">
      <div className="flex justify-between gap-32 p-6">
        <div className="w-2/3 flex flex-col gap-1">
          <Skeleton className="h-10" />
          <Skeleton className="h-6" />
        </div>
        <div className="w-1/3 flex flex-col gap-1">
          <Skeleton className="h-10" />
          <Skeleton className="h-6" />
        </div>
      </div>
      <SectionHeader>
        <div className="h-10"></div>
      </SectionHeader>
      <Skeleton className="h-1/2 mx-6 my-3" />
      <SectionHeader>
        <div className="h-10"></div>
      </SectionHeader>
      <Skeleton className="h-1/2 mx-6 my-3" />
    </div>
  )
}

export default LoadingQuery
