import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

import { buttonVariants } from '@/components/ui/button'
import UserPicture from '@/components/user/user-picture'
import UserSettingsPopover from '@/components/user/user-settings-popover'

import { Separator } from '@/components/ui/separator'
import { useAppContext } from '@/contexts/app-context'
import { cn } from '@/lib/utils'
import {
  Database,
  KeyRound,
  ListChecks,
  LucideIcon,
  Microscope,
  SlidersIcon,
  TerminalSquare,
} from 'lucide-react'

export interface MenuItem {
  text: string
  href: string
  icon: LucideIcon
  hidden?: boolean
}
export type MenuItems = MenuItem[]

const NAV_ITEMS: MenuItems = [
  {
    text: 'Queries',
    href: '/queries',
    icon: Microscope,
  },
  {
    text: 'Databases',
    href: '/databases',
    icon: Database,
  },
  {
    text: 'Golden SQL',
    href: '/golden-sql',
    icon: ListChecks,
  },
]
const CONFIG_NAV_ITEMS: MenuItems = [
  {
    text: 'Playground',
    href: '/playground',
    icon: TerminalSquare,
  },
  {
    text: 'Fine-tuning',
    href: '/fine-tuning',
    icon: SlidersIcon,
  },
  {
    text: 'API Keys',
    href: '/api-keys',
    icon: KeyRound,
  },
]

const SidebarNav = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLElement>) => {
  const pathname = usePathname()
  const { user, organization } = useAppContext()

  return (
    <aside className="min-w-[250px] flex flex-col justify-between bg-gray-50 border-r">
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
          {NAV_ITEMS.filter((i) => !i.hidden).map((item) => (
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
                  ? 'bg-black/10 hover:bg-black/10 font-bold'
                  : '',
                'justify-start',
                'gap-2',
                'px-5',
              )}
            >
              <item.icon />
              {item.text}
            </Link>
          ))}
          <Separator className="my-3" />
          {CONFIG_NAV_ITEMS.filter((i) => !i.hidden).map((item) => (
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
                  ? 'bg-black/10 hover:bg-black/10 font-bold'
                  : '',
                'justify-start',
                'gap-2',
                'px-5',
              )}
            >
              <item.icon />
              {item.text}
            </Link>
          ))}
        </nav>
      </div>
      {user && organization && (
        <div className="flex flex-col items-center  gap-3 p-3 m-3 border rounded-xl bg-white">
          <div className="w-full flex items-center justify-between gap-2 ">
            <div className="flex items-center gap-2">
              <UserPicture pictureUrl={user.picture} />
              <div className="flex flex-col">
                <span className="text-xs">{organization?.name}</span>{' '}
                <span className="font-semibold text-sm">{user.name}</span>
              </div>
            </div>
            <UserSettingsPopover user={user} organization={organization} />
          </div>
        </div>
      )}
    </aside>
  )
}

export default SidebarNav
