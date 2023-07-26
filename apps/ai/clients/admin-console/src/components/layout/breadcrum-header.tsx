import { cn } from '@/lib/utils'
import { useRouter } from 'next/router'

const BreadcrumbHeader = () => {
  const router = useRouter()
  const pathSegments = router.pathname
    .split('/')
    .filter(Boolean)
    .map((segment) => segment.replace('-', ' '))

  return (
    <header className="w-full p-5">
      <nav aria-label="Breadcrumb">
        <ol className="list-none p-0 inline-flex">
          {pathSegments.map((segment, idx) => (
            <li key={idx}>
              {idx > 0 && <span className="mx-4 text-gray-400">/</span>}
              <span
                className={cn(
                  idx === pathSegments.length - 1
                    ? 'text-black'
                    : 'text-gray-400',
                  'capitalize',
                  'font-bold',
                )}
              >
                {segment}
              </span>
            </li>
          ))}
        </ol>
      </nav>
    </header>
  )
}

export default BreadcrumbHeader
