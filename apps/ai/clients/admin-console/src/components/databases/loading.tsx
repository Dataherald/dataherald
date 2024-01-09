import { Skeleton } from '@/components/ui/skeleton'
import { Hourglass } from 'lucide-react'
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
  <>
    <div className="flex items-center gap-3 pt-2 pb-6">
      <Hourglass size={14} className="animate-spin" />
      <h1>
        Retrieving your Database... This can take up to 1 minute for large
        Databases...
      </h1>
    </div>
    <div className="space-y-5 px-3">
      <TreeNestedItemSkeleton />
      <TreeNestedItemSkeleton />
    </div>
  </>
)

export default LoadingDatabases
