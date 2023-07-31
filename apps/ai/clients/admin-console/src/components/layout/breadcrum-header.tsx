import { cn } from '@/lib/utils'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const BreadcrumbHeader = () => {
  const pathname = usePathname()
  const pathSegments =
    pathname
      ?.split('/')
      .filter(Boolean)
      .map((segment) => segment.replace('-', ' ')) || []

  return (
    <header className="w-full px-8 py-5">
      <nav aria-label="Breadcrumb">
        <ol className="list-none p-0 inline-flex">
          {pathSegments.map((segment, idx) => {
            const isLastSegment = idx === pathSegments.length - 1
            return (
              <li key={idx} className={cn('capitalize', 'font-bold')}>
                {idx > 0 && <span className="mx-4 text-gray-400">/</span>}
                {!isLastSegment ? (
                  <Link
                    href={`/${segment}`} // only supports one level for now
                    className={cn(
                      'font-normal',
                      'text-gray-400',
                      'hover:cursor-pointer',
                      'hover:text-primary',
                      'hover:underline',
                    )}
                  >
                    {segment}
                  </Link>
                ) : (
                  <span className="text-black">{segment}</span>
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
