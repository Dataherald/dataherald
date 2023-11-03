import {
  formatQueryStatusWithScore,
  getDomainStatus,
  getDomainStatusColors,
} from '@/lib/domain/query'
import { cn } from '@/lib/utils'
import { QueryStatus } from '@/models/api'
import { EDomainQueryStatus } from '@/models/domain'
import { Loader } from 'lucide-react'
import { FC, HTMLAttributes } from 'react'

export interface QueryMetadataProps extends HTMLAttributes<HTMLDivElement> {
  queryId: string
  status: QueryStatus
  confidenceLevel: number | null
  updatingQuery: boolean
  // onResubmit: () => void
}

const QueryMetadata: FC<QueryMetadataProps> = ({
  queryId,
  status,
  confidenceLevel,
  updatingQuery,
  // onResubmit,
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
  return (
    <div className={cn('flex flex-col gap-1 items-end', className)}>
      <div className="flex items-center gap-2">
        {/* <Button
          variant="ghost"
          className="flex items-center gap-2 h-9"
          onClick={onResubmit}
        >
          <Boxes /> Resubmit
        </Button> */}
        <h1 className="text-xl font-bold">{queryId}</h1>
      </div>
      <div
        className={cn(textColor, 'flex flex-row items-center font-semibold')}
      >
        {updatingQuery ? (
          <div className="text-slate-500 flex items-center gap-2">
            <Loader className="animate-spin" size={20} /> Updating query...
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
