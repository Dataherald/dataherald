import { cn, formatUrl } from '@/lib/utils'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useRouter } from 'next/router'
import { FC, HTMLAttributes } from 'react'

export type BreadcrumbHeaderProps = HTMLAttributes<HTMLHeadingElement>

const BreadcrumbHeader: FC<BreadcrumbHeaderProps> = ({ className }) => {
  const pathname = usePathname()
  const router = useRouter()
  const pathSegments = pathname?.split('/').filter(Boolean) || []
  const displayId = router.query.d_id

  if (displayId) {
    // Assumes the ID is the last segment
    pathSegments.pop() // Remove the actual ID
    pathSegments.push(displayId as string) // Add the display ID
  }

  return (
    <header className={cn(className, 'w-full px-6 py-4 shadow')}>
      <nav aria-label="Breadcrumb">
        <ol className="list-none p-0 inline-flex">
          {pathSegments.map((segment, idx) => {
            const isLastSegment = idx === pathSegments.length - 1
            return (
              <li
                key={idx}
                className={cn('first-letter:capitalize', 'font-bold')}
              >
                {idx > 0 && <span className="mx-4 text-slate-400">/</span>}
                {!isLastSegment ? (
                  <Link
                    href={`/${segment}`} // only supports one level for now
                    className={cn(
                      'text-slate-500',
                      'hover:cursor-pointer',
                      'hover:text-primary',
                      'hover:underline',
                    )}
                  >
                    {segment}
                  </Link>
                ) : (
                  <span className="text-black text-2xl">
                    {formatUrl(segment)}
                  </span>
                )}
              </li>
            )
          })}
        </ol>
      </nav>
    </header>
  )
}

export default BreadcrumbHeader
