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
import { useAppContext } from '@/contexts/app-context'
import { isEnterprise } from '@/lib/domain/billing'
import { cn } from '@/lib/utils'
import {
  ArrowUpRightIcon,
  BarChart2,
  BookOpenText,
  Building2,
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

  const FIRST_NAV_ITEMS: MenuItems = [
    {
      text: 'Playground',
      href: '/playground',
      icon: TerminalSquare,
    },
    {
      text: 'Databases',
      href: '/databases',
      icon: Database,
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

  const renderMenuItem = (item: MenuItem, newTab = false) => (
    <Link
      key={item.href}
      href={item.href}
      {...(newTab && { target: '_blank', rel: 'noopener noreferrer' })}
      className={cn(
        buttonVariants({ variant: 'ghost' }),
        pathname?.includes(item.href)
          ? 'bg-slate-300 hover:bg-slate-300 text-slate-900 font-semibold'
          : 'hover:bg-slate-200',
        'text-sm',
        'justify-start',
        'px-3',
      )}
    >
      {item.icon ? (
        <item.icon
          size={18}
          strokeWidth={pathname?.includes(item.href) ? 2.5 : 1.8}
        />
      ) : item.imageURL ? (
        <Image src={item.imageURL} alt={item.text} width={18} height={18} />
      ) : null}
      <span className="ml-2">{item.text}</span>
      {item.external && (
        <ArrowUpRightIcon className="pb-0.5" size={12} strokeWidth={1.8} />
      )}
    </Link>
  )

  const handleLogout = logout

  return (
    <aside className="min-w-[200px] pt-1 flex flex-col justify-between bg-slate-50 border-r shadow-sm">
      <div className="flex flex-col gap-5">
        <Image
          priority
          src="/images/dh_ai_logo.svg"
          alt="Dataherald AI Logo"
          width={150}
          height={50}
          className="w-full px-3 py-5"
        ></Image>
        <nav className={cn('flex flex-col', className)} {...props}>
          {FIRST_NAV_ITEMS.filter((i) => !i.hidden).map((item) =>
            renderMenuItem(item),
          )}
          <Separator className="my-3" />
          {SECOND_NAV_ITEMS.filter((i) => !i.hidden).map((item) =>
            renderMenuItem(item),
          )}
        </nav>
      </div>
      <div className="flex flex-col">
        {BOTTOM_NAV_ITEMS.filter((i) => !i.hidden).map((item) =>
          renderMenuItem(item, true),
        )}

        {user && (
          <Popover>
            <PopoverTrigger asChild>
              <div className="flex flex-col items-center  gap-3 p-3 m-2 border rounded-xl bg-white cursor-pointer">
                <div className="w-full flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <UserPicture pictureUrl={user.picture} />
                    <div className="flex flex-col break-all">
                      <span className="text-xs">{organization?.name}</span>{' '}
                      <span className="font-semibold text-sm">{user.name}</span>
                    </div>
                  </div>
                </div>
              </div>
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
  )
}

export default SidebarNav
