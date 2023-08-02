import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { formatQueryStatus } from '@/lib/domain/query-status'
import { cn } from '@/lib/utils'
import { EQueryStatus, QueryStatus } from '@/models/api'
import { CheckCircle, XCircle } from 'lucide-react'
import { FC } from 'react'

export interface QueryVerifySelectProps {
  verifiedStatus: QueryStatus
  onValueChange: (value: QueryStatus) => void
}

const QueryVerifySelect: FC<QueryVerifySelectProps> = ({
  verifiedStatus,
  onValueChange,
}) => {
  const handleValueChange = (value: QueryStatus) => {
    onValueChange(value)
  }

  const verifiedOptionDisplay: JSX.Element = (
    <div className="flex items-center gap-3 capitalize font-semibold text-green-700">
      <CheckCircle strokeWidth={2.5} />
      {formatQueryStatus(EQueryStatus.VERIFIED)}
    </div>
  )
  const notVerifiedOptionDisplay: JSX.Element = (
    <div className="flex items-center gap-3 capitalize font-semibold text-red-500">
      <XCircle strokeWidth={2.5} />
      {formatQueryStatus(EQueryStatus.NOT_VERIFIED)}
    </div>
  )
  return (
    <Select onValueChange={handleValueChange}>
      <SelectTrigger
        className={cn(
          'w-[180px]',
          verifiedStatus === EQueryStatus.VERIFIED
            ? 'border-green-700'
            : 'border-red-500',
        )}
      >
        {verifiedStatus === EQueryStatus.VERIFIED ? (
          <SelectValue placeholder={verifiedOptionDisplay} />
        ) : (
          <SelectValue placeholder={notVerifiedOptionDisplay} />
        )}
      </SelectTrigger>
      <SelectContent>
        {Object.values(EQueryStatus)
          .filter((qs: QueryStatus) => qs !== EQueryStatus.SQL_ERROR)
          .map((qs: QueryStatus, idx) =>
            qs === EQueryStatus.VERIFIED ? (
              <SelectItem
                key={qs + idx}
                value={qs}
                className="focus:bg-green-100"
              >
                {verifiedOptionDisplay}
              </SelectItem>
            ) : (
              <SelectItem
                key={qs + idx}
                value={qs}
                className="focus:bg-red-100"
              >
                {notVerifiedOptionDisplay}
              </SelectItem>
            ),
          )}
      </SelectContent>
    </Select>
  )
}

export default QueryVerifySelect
