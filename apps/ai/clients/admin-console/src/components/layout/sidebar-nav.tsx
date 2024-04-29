import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

import { Button, buttonVariants } from '@/components/ui/button'
import UserPicture from '@/components/user/user-picture'

import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Separator } from '@/components/ui/separator'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { useAppContext } from '@/contexts/app-context'
import { useUI } from '@/contexts/ui-context'
import { isEnterprise } from '@/lib/domain/billing'
import { cn } from '@/lib/utils'
import {
  ArrowUpRightIcon,
  BarChart2,
  BookOpenText,
  Building2,
  ChevronsLeft,
  ChevronsRight,
  Database,
  KeyRound,
  Landmark,
  LogOut,
  LucideIcon,
  MessagesSquare,
  ShieldCheck,
  ShieldQuestion,
  SlidersIcon,
  TerminalSquare,
  UserRound,
} from 'lucide-react'
import { Fragment } from 'react'

export interface MenuItem {
  text: string
  href: string
  icon?: LucideIcon
  imageURL?: string
  external?: boolean
  hidden?: boolean
}
export type MenuItems = MenuItem[]

const SidebarNav = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLElement>) => {
  const pathname = usePathname()
  const { user, organization, logout } = useAppContext()
  const { sidebarOpen: isSidebarOpen, setSidebarOpen: setIsSidebarOpen } =
    useUI()

  const FIRST_NAV_ITEMS: MenuItems = [
    {
      text: 'Databases',
      href: '/databases',
      icon: Database,
    },
    {
      text: 'Playground',
      href: '/playground',
      icon: TerminalSquare,
    },
    {
      text: 'Queries',
      href: '/queries',
      icon: ShieldQuestion,
    },
    {
      text: 'Golden SQL',
      href: '/golden-sql',
      icon: ShieldCheck,
    },
    {
      text: 'Fine-tuning',
      href: '/fine-tuning',
      icon: SlidersIcon,
    },
  ]
  const SECOND_NAV_ITEMS: MenuItems = [
    {
      text: 'API keys',
      href: '/api-keys',
      icon: KeyRound,
    },
    {
      text: 'Usage',
      href: '/usage',
      icon: BarChart2,
      hidden: isEnterprise(organization),
    },
    {
      text: 'Billing',
      href: '/billing',
      icon: Landmark,
      hidden: isEnterprise(organization),
    },
    {
      text: 'Organization',
      href: '/organization',
      icon: Building2,
    },
  ]

  const BOTTOM_NAV_ITEMS: MenuItems = [
    {
      text: 'Community',
      href: 'https://discord.gg/tmTpvw9U',
      icon: MessagesSquare,
      external: true,
    },
    {
      text: 'Documentation',
      href: 'https://docs.dataherald.com/',
      icon: BookOpenText,
      external: true,
    },
  ]

  const withTooltip = (
    menuItem: JSX.Element,
    tooltipContent: JSX.Element,
  ): JSX.Element => (
    <Tooltip delayDuration={100}>
      <TooltipTrigger asChild>{menuItem}</TooltipTrigger>
      <TooltipContent>{tooltipContent}</TooltipContent>
    </Tooltip>
  )

  const renderMenuItem = (item: MenuItem): JSX.Element => (
    <Link
      href={item.href}
      {...(item.external && { target: '_blank', rel: 'noopener noreferrer' })}
      className={cn(
        buttonVariants({ variant: 'ghost', size: 'icon' }),
        pathname?.includes(item.href) &&
          'bg-slate-300 hover:bg-slate-300 text-slate-900 font-semibold',
        isSidebarOpen && 'justify-stretch',
        'h-8 text-sm group items-stretch',
      )}
    >
      {item.icon ? (
        <item.icon
          size={18}
          strokeWidth={pathname?.includes(item.href) ? 2.5 : 1.8}
          className="shrink-0 group-hover:scale-110 transition-transform duration-300 ease-in-out"
        />
      ) : item.imageURL ? (
        <Image src={item.imageURL} alt={item.text} width={18} height={18} />
      ) : null}
      <>
        <span
          className={cn(
            'ml-2 group-hover:font-semibold whitespace-nowrap',
            isSidebarOpen ? 'flex' : 'hidden',
          )}
        >
          {item.text}
        </span>
        {item.external && isSidebarOpen && (
          <ArrowUpRightIcon className="pb-0.5" size={12} strokeWidth={1.8} />
        )}
      </>
    </Link>
  )

  const renderMenuItems = (items: MenuItems): JSX.Element => (
    <>
      {items
        .filter((i) => !i.hidden)
        .map((item, idx) => (
          <Fragment key={idx}>
            {isSidebarOpen
              ? renderMenuItem(item)
              : withTooltip(
                  renderMenuItem(item),
                  <div className="flex items-center">
                    <span>{item.text}</span>
                    {item.external && (
                      <div>
                        <ArrowUpRightIcon
                          size={14}
                          strokeWidth={1.8}
                          className="pb-1"
                        />
                      </div>
                    )}
                  </div>,
                )}
          </Fragment>
        ))}
    </>
  )

  const handleLogout = logout

  return (
    <TooltipProvider>
      <aside
        className={cn(
          'flex flex-col items-center justify-between bg-slate-50 border-r shadow py-2 px-1',
          isSidebarOpen
            ? 'items-stretch w-52 transition-width duration-200 ease-in-out'
            : 'w-11',
        )}
      >
        <div className={cn('flex flex-col items-stretch gap-8')}>
          <div className={cn('h-12', isSidebarOpen ? 'w-[150px]' : 'w-6')}>
            <Image
              priority
              src="/images/dh-logo-color.svg"
              alt="Dataherald Logo"
              width={150}
              height={50}
              className={cn(
                'w-full px-1 py-3',
                isSidebarOpen ? 'd-block' : 'hidden',
              )}
            ></Image>
            <Image
              priority
              src="/images/dh-logo-symbol-color.svg"
              alt="Dataherald Symbol Logo"
              width={22}
              height={22}
              className={cn('mx-1 my-3', isSidebarOpen ? 'hidden' : 'd-block')}
            ></Image>
          </div>
          <nav className={cn('flex flex-col gap-0.5', className)} {...props}>
            {renderMenuItems(FIRST_NAV_ITEMS)}
            <Separator className="my-3" />
            {renderMenuItems(SECOND_NAV_ITEMS)}
          </nav>
        </div>
        <div
          className={cn(
            'flex flex-col items-center',
            isSidebarOpen && 'items-stretch',
          )}
        >
          {isSidebarOpen ? (
            <Button variant="ghost" onClick={() => setIsSidebarOpen(false)}>
              <ChevronsLeft size={18} strokeWidth={1.8} />
            </Button>
          ) : (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSidebarOpen(true)}
            >
              <ChevronsRight size={18} strokeWidth={1.8} />
            </Button>
          )}
          {renderMenuItems(BOTTOM_NAV_ITEMS)}
          {user && (
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="icon"
                  size={isSidebarOpen ? 'default' : 'icon'}
                  className={cn('p-1 flex items-center justify-stretch w-full')}
                >
                  <UserPicture size={24} pictureUrl={user.picture} />
                  {isSidebarOpen && (
                    <span className="ml-2 font-medium text-sm whitespace-nowrap">
                      {user.name}
                    </span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="flex flex-col gap-2 ml-3 p-3 w-[250px] max-w-sm text-center">
                <div className="flex items-center justify-center gap-2">
                  <div className="flex flex-col items-center mt-1.5 break-all">
                    <span className="text-xs text-slate-500">{user.email}</span>
                    <span className="text-sm text-slate-900">
                      {organization?.name}
                    </span>
                  </div>
                </div>
                <div className="flex flex-col items-center justify-center gap-2 p-1">
                  <h1>Hi, {user.name}!</h1>
                  <UserPicture pictureUrl={user.picture} size={75} />
                </div>
                <Link href="/my-account">
                  <Button variant="ghost" size="sm" className="w-full">
                    <UserRound className="mr-2" size={18} /> My account
                  </Button>
                </Link>
                <Separator />
                <Button
                  variant="destructive-outline"
                  size="sm"
                  onClick={handleLogout}
                >
                  <LogOut className="mr-2" size={18} />
                  Sign out
                </Button>
              </PopoverContent>
            </Popover>
          )}
        </div>
      </aside>
    </TooltipProvider>
  )
}

export default SidebarNav
