import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

import { buttonVariants } from '@/components/ui/button'
import UserPicture from '@/components/user/user-picture'
import UserSettingsPopover from '@/components/user/user-settings-popover'

import { cn } from '@/lib/utils'
import { User } from '@/models/api'
import { useUser } from '@auth0/nextjs-auth0/client'
import { Cable, Database, LucideIcon, Microscope } from 'lucide-react'

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
    text: 'Context Stores',
    href: '/context-stores',
    icon: Cable,
  },
]

const SidebarNav = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLElement>) => {
  const pathname = usePathname()
  const { user: authUser } = useUser()
  const user = authUser as User
  const {
    name,
    picture,
    organization: { name: orgName },
  } = user as User

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
        </nav>
      </div>
      {user && (
        <div className="flex items-center justify-between gap-2 p-3 m-3 border rounded-xl bg-white">
          <div className="flex items-center gap-2">
            <UserPicture pictureUrl={picture} />
            <div className="flex flex-col">
              <span className="text-xs">{orgName}</span>{' '}
              <span className="font-semibold text-sm">{name}</span>
            </div>
          </div>
          <UserSettingsPopover user={user} />
        </div>
      )}
    </aside>
  )
}

export default SidebarNav
