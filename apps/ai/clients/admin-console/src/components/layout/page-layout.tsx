import BreadcrumbHeader from '@/components/layout/breadcrum-header'
import SidebarNav from '@/components/layout/sidebar-nav'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { FC, HTMLAttributes } from 'react'

export type PageLayoutProps = HTMLAttributes<HTMLDivElement>

const PageLayout: FC<PageLayoutProps> = ({
  className,
  children,
  ...props
}: PageLayoutProps) => (
  <div className={cn('flex h-screen', className)} {...props}>
    <SidebarNav />
    <div className="w-full h-full overflow-auto flex flex-col">
      <BreadcrumbHeader />
      <Separator />
      <main className="grow flex flex-col overflow-auto p-6">{children}</main>
    </div>
  </div>
)

export default PageLayout
