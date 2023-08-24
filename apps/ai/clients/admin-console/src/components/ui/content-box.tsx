import { cn } from '@/lib/utils'

function ContentBox({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'grow flex flex-col gap-4 rounded-xl border bg-gray-50 p-6',
        className,
      )}
      {...props}
    />
  )
}

export { ContentBox }
