import { Skeleton } from '@/components/ui/skeleton'
import { FC, ReactNode } from 'react'

const TreeItemSkeleton: FC = () => (
  <div className="flex items-center space-x-2">
    <Skeleton className="w-6 h-6" />
    <Skeleton className="w-64 h-4" />
  </div>
)

const TreeNestedItemSkeleton: FC<{ children?: ReactNode }> = ({ children }) => (
  <div className="space-y-4">
    <TreeItemSkeleton />
    <div className="pl-4 space-y-3">
      <TreeItemSkeleton />
      <TreeItemSkeleton />
      {children}
    </div>
  </div>
)

const LoadingDatabases: FC = () => (
  <>
    <Skeleton className="w-44 h-6" />
    <div className="space-y-5">
      <TreeNestedItemSkeleton>
        <TreeNestedItemSkeleton />
      </TreeNestedItemSkeleton>
      <TreeNestedItemSkeleton>
        <TreeNestedItemSkeleton />
      </TreeNestedItemSkeleton>
    </div>
  </>
)

export default LoadingDatabases
