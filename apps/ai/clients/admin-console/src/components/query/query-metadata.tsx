import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import {
  formatQueryStatusWithScore,
  getDomainStatus,
  getDomainStatusColors,
  isRejected,
  isVerified,
} from '@/lib/domain/query'
import { cn } from '@/lib/utils'
import { QueryStatus } from '@/models/api'
import { EDomainQueryStatus } from '@/models/domain'
import { Ban, Bot, Loader } from 'lucide-react'
import { FC, HTMLAttributes } from 'react'

export interface QueryMetadataProps extends HTMLAttributes<HTMLDivElement> {
  promptId: string
  status: QueryStatus
  confidenceLevel: number | null
  updatingQuery?: boolean
  onResubmit?: () => void
}

const QueryMetadata: FC<QueryMetadataProps> = ({
  promptId,
  status,
  confidenceLevel,
  updatingQuery,
  onResubmit,
  className,
}) => {
  const textColor = getDomainStatusColors(status, confidenceLevel).text
  const domainStatus = getDomainStatus(status, confidenceLevel)
  const statusText = formatQueryStatusWithScore(domainStatus, confidenceLevel)
  const isFromAI = [
    EDomainQueryStatus.LOW_CONFIDENCE.valueOf(),
    EDomainQueryStatus.MEDIUM_CONFIDENCE.valueOf(),
    EDomainQueryStatus.HIGH_CONFIDENCE.valueOf(),
  ].includes(domainStatus as EDomainQueryStatus)
  const isNotVerified = !isVerified(status) && !isRejected(status)
  return (
    <div className={cn('flex flex-col gap-1 items-end', className)}>
      <div className="flex items-center gap-2">
        {onResubmit && (
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button
                variant="ghost"
                disabled={updatingQuery}
                className="flex items-center gap-2 h-9"
              >
                <Bot size={16} strokeWidth={2} />
                Resubmit
              </Button>
            </AlertDialogTrigger>

            {isNotVerified ? (
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Resubmit Query</AlertDialogTitle>
                </AlertDialogHeader>
                <AlertDialogDescription>
                  The AI platform will generate an entire new response for the
                  question. The process can take a couple of minutes.
                </AlertDialogDescription>
                <AlertDialogDescription>
                  Do you wish to continue?
                </AlertDialogDescription>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={onResubmit}>
                    <Bot size={16} className="mr-2" />
                    Resubmit
                  </AlertDialogAction>
                </AlertDialogFooter>{' '}
              </AlertDialogContent>
            ) : (
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>
                    <div className="flex items-center gap-2">
                      <Ban size={22} strokeWidth={2.5} />
                      {`Can't Resubmit Query`}
                    </div>
                  </AlertDialogTitle>
                </AlertDialogHeader>
                <AlertDialogDescription>
                  This query was already{' '}
                  <strong>
                    {isVerified(status) ? 'Verified' : 'Rejected'}
                  </strong>{' '}
                  by an administrator. If you wish to resubmit the query to the
                  platform to get a new response, please mark the query as{' '}
                  <strong>Not Verified</strong> first.
                </AlertDialogDescription>
                <AlertDialogFooter>
                  <AlertDialogCancel>Close</AlertDialogCancel>
                </AlertDialogFooter>
              </AlertDialogContent>
            )}
          </AlertDialog>
        )}
        <h1 className="text-xl font-bold">{promptId}</h1>
      </div>
      <div
        className={cn(textColor, 'flex flex-row items-center font-semibold')}
      >
        {updatingQuery ? (
          <div className="text-slate-500 flex items-center gap-2">
            <Loader className="animate-spin" size={20} /> Updating query
          </div>
        ) : (
          <>
            <div className="w-2 h-2 mr-2 rounded-full bg-current shrink-0" />
            {isFromAI ? `Not Verified - ` : ''} {statusText}
          </>
        )}
      </div>
    </div>
  )
}

export default QueryMetadata
