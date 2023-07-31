import { cn } from '@/lib/utils'
import { FC, HTMLAttributes } from 'react'
import { Separator } from '../ui/separator'
import BreadcrumbHeader from './breadcrum-header'
import SidebarNav from './sidebar-nav'

export type PageLayoutProps = HTMLAttributes<HTMLDivElement>

const PageLayout: FC<PageLayoutProps> = ({
  className,
  children,
  ...props
}: PageLayoutProps) => {
  return (
    <div className={cn('flex h-screen overflow-hidden', className)} {...props}>
      <SidebarNav />
      <div className="flex-1">
        <BreadcrumbHeader />
        <Separator />
        <main className="overflow-auto">{children}</main>
      </div>
    </div>
  )
}

export default PageLayout
