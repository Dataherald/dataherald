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
  BarChart2,
  BookOpenText,
  Building2,
  Database,
  HelpCircle,
  KeyRound,
  Landmark,
  LogOut,
  LucideIcon,
  ShieldCheck,
  ShieldQuestion,
  SlidersIcon,
  TerminalSquare,
  UserRound,
} from 'lucide-react'

export interface MenuItem {
  text: string
  href: string
  icon: LucideIcon
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
      text: 'Help',
      href: 'https://www.dataherald.com/contact',
      icon: HelpCircle,
    },
    {
      text: 'Documentation',
      href: 'https://docs.dataherald.com/',
      icon: BookOpenText,
    },
  ]

  const handleLogout = logout

  return (
    <aside className="min-w-[220px] flex flex-col justify-between bg-gray-50 border-r">
      <div className="flex flex-col gap-5">
        <Image
          priority
          src="/images/dh_ai_logo.svg"
          alt="Dataherald AI Logo"
          width={150}
          height={50}
          className="w-full p-5"
        ></Image>
        <nav className={cn('flex flex-col', className)} {...props}>
          {FIRST_NAV_ITEMS.filter((i) => !i.hidden).map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                buttonVariants({ variant: 'secondary-outline' }),
                'bg-gray-50',
                'hover:bg-gray-200',
                'border-none',
                'font-normal',
                pathname?.includes(item.href)
                  ? 'bg-black/10 hover:bg-black/10 font-semibold'
                  : '',
                'justify-start',
                'gap-2',
                'px-5',
              )}
            >
              <item.icon strokeWidth={1.5} />
              {item.text}
            </Link>
          ))}
          <Separator className="my-3" />
          {SECOND_NAV_ITEMS.filter((i) => !i.hidden).map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                buttonVariants({ variant: 'secondary-outline' }),
                'bg-gray-50',
                'hover:bg-gray-200',
                'border-none',
                'font-normal',
                pathname?.includes(item.href)
                  ? 'bg-black/10 hover:bg-black/10 font-semibold'
                  : '',
                'justify-start',
                'gap-2',
                'px-5',
              )}
            >
              <item.icon strokeWidth={1.5} />
              {item.text}
            </Link>
          ))}
        </nav>
      </div>
      <div className="flex flex-col">
        {BOTTOM_NAV_ITEMS.filter((i) => !i.hidden).map((item) => (
          <Link
            key={item.href}
            target="_blank"
            rel="noopener noreferrer"
            href={item.href}
            className={cn(
              buttonVariants({ variant: 'secondary-outline' }),
              'bg-gray-50',
              'hover:bg-gray-200',
              'border-none',
              'font-normal',
              pathname?.includes(item.href)
                ? 'bg-black/10 hover:bg-black/10 font-semibold'
                : '',
              'justify-start',
              'gap-2',
              'px-5',
            )}
          >
            <item.icon strokeWidth={1.5} />
            {item.text}
          </Link>
        ))}

        {user && (
          <Popover>
            <PopoverTrigger asChild>
              <div className="flex flex-col items-center  gap-3 p-3 m-3 border rounded-xl bg-white cursor-pointer">
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
            <PopoverContent className="flex flex-col gap-3 ml-3 p-3">
              <div className="flex items-center justify-center gap-3">
                <div className="flex flex-col items-center gap-2 mt-1.5 break-all">
                  <span className="text-xs text-slate-500">{user.email}</span>
                  <span className="text-sm text-slate-900">
                    {organization?.name}
                  </span>
                </div>
              </div>
              <div className="flex flex-col items-center justify-center gap-3 p-2">
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
