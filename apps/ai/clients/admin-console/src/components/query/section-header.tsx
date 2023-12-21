import { cn } from '@/lib/utils'
import { FC, ReactNode } from 'react'

export const SectionHeader: FC<{ children: ReactNode; className?: string }> = ({
  children,
  className = '',
}) => (
  <div
    className={cn(
      'bg-slate-200 w-full px-6 py-3 flex items-center justify-between gap-2',
      className,
    )}
  >
    {children}
  </div>
)

export const SectionHeaderTitle: FC<{
  children: ReactNode
  className?: string
}> = ({ children, className = '' }) => (
  <div className={cn('flex items-center gap-3 font-bold text-lg', className)}>
    {children}
  </div>
)
