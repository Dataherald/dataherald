import { cn } from '@/lib/utils'
import { Separator } from '../ui/separator'
import BreadcrumbHeader from './breadcrum-header'
import SidebarNav from './sidebar-nav'

export type LayoutProps = React.ButtonHTMLAttributes<HTMLDivElement>

const Layout = ({ className, children, ...props }: LayoutProps) => {
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

export default Layout
