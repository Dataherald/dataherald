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
    <aside className="flex flex-col gap-8 bg-gray-100">
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
              'bg-gray-100',
              'hover:bg-gray-300',
              'border-none',
              pathname === item.href
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
