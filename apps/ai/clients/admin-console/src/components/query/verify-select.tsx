import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  QUERY_STATUS_COLORS,
  formatQueryStatus,
  isNotVerified,
  isRejected,
  isVerified,
} from '@/lib/domain/query'
import { cn } from '@/lib/utils'
import { QueryStatus } from '@/models/api'
import {
  EDomainQueryWorkspaceStatus,
  QueryWorkspaceStatus,
} from '@/models/domain'
import { Ban, CheckCircle, XCircle } from 'lucide-react'
import { FC, useCallback } from 'react'

export interface QueryVerifySelectProps {
  verificationStatus: QueryWorkspaceStatus
  onValueChange: (value: QueryWorkspaceStatus) => void
}

const QueryVerifySelect: FC<QueryVerifySelectProps> = ({
  verificationStatus,
  onValueChange,
}) => {
  const handleValueChange = (value: QueryWorkspaceStatus) => {
    onValueChange(value)
  }

  const getStatusDisplay = useCallback(
    (status: QueryWorkspaceStatus) => (
      <div
        className={cn(
          'flex items-center gap-3 font-semibold text-base',
          QUERY_STATUS_COLORS[status].text,
        )}
      >
        {isVerified(status) && <CheckCircle size={20} strokeWidth={2.5} />}
        {isNotVerified(status) && <XCircle size={20} strokeWidth={2.5} />}
        {isRejected(status) && <Ban size={20} strokeWidth={3} />}
        {formatQueryStatus(status)}
      </div>
    ),
    [],
  )

  return (
    <Select onValueChange={handleValueChange}>
      <SelectTrigger
        className={cn(
          'w-[180px]',
          QUERY_STATUS_COLORS[verificationStatus].border,
        )}
      >
        <SelectValue placeholder={getStatusDisplay(verificationStatus)} />
      </SelectTrigger>
      <SelectContent>
        {Object.values(EDomainQueryWorkspaceStatus).map(
          (qs: QueryWorkspaceStatus, idx) => (
            <SelectItem
              key={qs + idx}
              value={qs}
              className={`focus:${QUERY_STATUS_COLORS[qs].background}`}
            >
              {getStatusDisplay(qs)}
            </SelectItem>
          ),
        )}
      </SelectContent>
    </Select>
  )
}

export default QueryVerifySelect
