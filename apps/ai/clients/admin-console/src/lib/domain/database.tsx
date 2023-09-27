import { ETableSyncStatus, TableSyncStatus } from '@/models/api'
import { EDomainTableSyncStatusTextColor } from '@/models/domain'
import {
  Check,
  CircleSlash,
  LucideIcon,
  RefreshCcw,
  ShieldAlert,
  XCircle,
} from 'lucide-react'

export const formatDriver = (driver: string) => `${driver}://`

export const getDomainTableSyncStatusColor = (
  sync_status: TableSyncStatus,
): EDomainTableSyncStatusTextColor => {
  return EDomainTableSyncStatusTextColor[sync_status]
}

export const isSelectableByStatus = (sync_status: TableSyncStatus): boolean =>
  [
    ETableSyncStatus.NOT_SYNCHRONIZED,
    ETableSyncStatus.FAILED,
    ETableSyncStatus.SYNCHRONIZED,
  ].includes(ETableSyncStatus[sync_status])

export const getDomainTableSyncStatusIcon = (
  sync_status: TableSyncStatus,
): LucideIcon | null => {
  switch (sync_status) {
    case ETableSyncStatus.SYNCHRONIZED:
      return Check
    case ETableSyncStatus.SYNCHRONIZING:
      return RefreshCcw
    case ETableSyncStatus.NOT_SYNCHRONIZED:
      return CircleSlash
    case ETableSyncStatus.DEPRECATED:
      return ShieldAlert
    case ETableSyncStatus.FAILED:
      return XCircle
    default:
      return null
  }
}

export const formatTableSyncStatus = (sync_status: TableSyncStatus): string => {
  return sync_status?.replace('_', ' ').toLowerCase()
}
