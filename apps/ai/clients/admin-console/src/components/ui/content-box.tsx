import { cn } from '@/lib/utils'

function ContentBox({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'grow flex flex-col gap-4 rounded-xl border border-slate-200 bg-slate-50 p-6 shadow-sm',
        className,
      )}
      {...props}
    />
  )
}

export { ContentBox }
