import ErrorDetails from '@/components/error/error-details'
import { Toaster } from '@/components/ui/toaster'
import { ErrorResponse } from '@/models/api'
import { AlertOctagon } from 'lucide-react'
import { FC, HTMLAttributes } from 'react'

export type PageErrorMessageProps = HTMLAttributes<HTMLDivElement> & {
  message: string
  error?: ErrorResponse
}

const PageErrorMessage: FC<PageErrorMessageProps> = ({
  message,
  error,
  ...props
}) => (
  <div className="flex flex-col gap-5 text-sm text-slate-500" {...props}>
    <div className="flex items-center gap-2">
      <AlertOctagon size={18} strokeWidth={2.5} />
      <span className="font-semibold">{message}</span>
    </div>
    {error && <ErrorDetails error={error} />}
    <Toaster />
  </div>
)

export default PageErrorMessage
