import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'
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

  return (
    <aside className="w-60 flex flex-col gap-8 bg-gray-50 border-r">
      <Image
        priority
        src="/images/dh_ai_logo.svg"
        alt="Dataherald AI Logo"
        width={150}
        height={50}
        className="w-full px-4 py-5"
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
              'py-2',
            )}
          >
            <item.icon />
            {item.text}
          </Link>
        ))}
      </nav>
    </aside>
  )
}

export default SidebarNav
