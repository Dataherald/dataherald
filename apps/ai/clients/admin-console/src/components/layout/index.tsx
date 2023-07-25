import { ReactNode } from 'react'
import { Separator } from '../ui/separator'
import BreadcrumbHeader from './breadcrum-header'
import SidebarNav from './sidebar-nav'

type LayoutProps = {
  children: ReactNode
}

const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="flex h-screen overflow-hidden">
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
