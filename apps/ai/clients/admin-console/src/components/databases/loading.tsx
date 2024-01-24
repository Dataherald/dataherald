import { ContentBox } from '@/components/ui/content-box'
import { Skeleton } from '@/components/ui/skeleton'
import { Loader } from 'lucide-react'
import { FC, ReactNode } from 'react'

const TreeItemSkeleton: FC = () => (
  <div className="flex items-center space-x-2">
    <Skeleton className="w-6 h-6" />
    <Skeleton className="w-full h-4" />
  </div>
)

const TreeNestedItemSkeleton: FC<{ children?: ReactNode }> = ({ children }) => (
  <div className="space-y-4">
    <TreeItemSkeleton />
    <div className="pl-14 space-y-3">
      <TreeItemSkeleton />
      <TreeItemSkeleton />
      <TreeItemSkeleton />
      <TreeItemSkeleton />
      <TreeItemSkeleton />
      {children}
    </div>
  </div>
)

const LoadingDatabases: FC = () => (
  <div className="grow flex flex-col m-6">
    <div className="flex items-center gap-2 pt-2 pb-6">
      <Loader size={18} className="animate-spin" />
      <h1>
        Retrieving your Databases. This can take up to 1 minute for large
        Databases.
      </h1>
    </div>
    <ContentBox className="grow flex flex-col gap-4 p-6">
      <div className="flex items-center justify-between py-4 gap-2">
        <Skeleton className="w-1/5 h-6" />
        <Skeleton className="w-2/5 h-6" />
      </div>
      <div className="space-y-5 px-3">
        <TreeNestedItemSkeleton />
        <TreeNestedItemSkeleton />
      </div>
    </ContentBox>
  </div>
)

export default LoadingDatabases
