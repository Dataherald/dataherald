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
import { EQueryStatus, QueryStatus } from '@/models/api'
import { Ban, CheckCircle, XCircle } from 'lucide-react'
import { FC, useCallback } from 'react'

export interface QueryVerifySelectProps {
  verificationStatus: QueryStatus
  onValueChange: (value: QueryStatus) => void
}

const QueryVerifySelect: FC<QueryVerifySelectProps> = ({
  verificationStatus,
  onValueChange,
}) => {
  const handleValueChange = (value: QueryStatus) => {
    onValueChange(value)
  }

  const getStatusDisplay = useCallback(
    (status: QueryStatus) => (
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
        {Object.values(EQueryStatus)
          .filter((qs: QueryStatus) => qs !== EQueryStatus.SQL_ERROR)
          .map((qs: QueryStatus, idx) => (
            <SelectItem
              key={qs + idx}
              value={qs}
              className={`focus:${QUERY_STATUS_COLORS[qs].background}`}
            >
              {getStatusDisplay(qs)}
            </SelectItem>
          ))}
      </SelectContent>
    </Select>
  )
}

export default QueryVerifySelect
