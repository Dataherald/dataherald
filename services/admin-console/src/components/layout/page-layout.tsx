import BreadcrumbHeader from '@/components/layout/breadcrum-header'
import LoadingPage from '@/components/layout/loading-page'
import SidebarNav from '@/components/layout/sidebar-nav'
import { Separator } from '@/components/ui/separator'
import { useAppContext } from '@/contexts/app-context'
import { cn } from '@/lib/utils'
import { FC, HTMLAttributes } from 'react'

interface PageLayoutProps extends HTMLAttributes<HTMLDivElement> {
  disableBreadcrumb?: boolean
}

const PageLayout: FC<PageLayoutProps> = ({
  className,
  children,
  disableBreadcrumb = false,
  ...props
}: PageLayoutProps) => {
  const { user, organization } = useAppContext()

  return (
    <div className={cn('flex h-screen', className)} {...props}>
      {!user || !organization ? (
        <LoadingPage />
      ) : (
        <>
          <SidebarNav />
          <div className="w-full h-full overflow-auto flex flex-col">
            {!disableBreadcrumb && <BreadcrumbHeader />}
            <Separator />
            <main className="grow flex flex-col overflow-auto">{children}</main>
          </div>
        </>
      )}
    </div>
  )
}

export default PageLayout
