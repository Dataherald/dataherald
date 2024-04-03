import { Button } from '@/components/ui/button'
import { toast } from '@/components/ui/use-toast'
import { cn, copyToClipboard } from '@/lib/utils'
import { ErrorResponse } from '@/models/api'
import { Copy } from 'lucide-react'
import { FC, HTMLAttributes } from 'react'

type ErrorDetailsProps = HTMLAttributes<HTMLDivElement> & {
  error: ErrorResponse
  size?: 'default' | 'small'
  displayTitle?: boolean
}

const ErrorDetails: FC<ErrorDetailsProps> = ({
  error,
  displayTitle = true,
  size = 'default',
  className,
  ...props
}) => {
  const handleCopyErrorTraceId = async () => {
    try {
      await copyToClipboard(error?.trace_id)
      toast({
        variant: 'success',
        title: 'Error Trace ID copied!',
      })
    } catch (error) {
      console.error('Could not copy text: ', error)
      toast({
        variant: 'destructive',
        title: 'Could not copy the Error Trace ID',
      })
    }
  }

  const isSmall = size === 'small'

  return (
    <div
      className={cn(
        'flex flex-col gap-2 max-w-fit',
        isSmall ? 'text-xs' : 'text-sm',
        className,
      )}
      {...props}
    >
      {displayTitle && <span className="font-semibold">Error details</span>}
      {error.trace_id && (
        <div className="flex items-center gap-2">
          <span className="font-semibold">Trace ID:</span>
          <span>{error.trace_id}</span>
          <Button
            type="button"
            variant="icon"
            className="p-0 h-fit text-slate-500"
            onClick={handleCopyErrorTraceId}
          >
            <Copy size={isSmall ? 12 : 14} strokeWidth={2} />
          </Button>
        </div>
      )}
      <div className="flex items-start gap-2">
        <span className="font-semibold">Message:</span>
        <span>{error.message}</span>
      </div>
      {error.description && (
        <div className="flex items-start gap-2">
          <span className="font-semibold">Message:</span>
          <span>{error.description}</span>
        </div>
      )}
    </div>
  )
}

export default ErrorDetails
