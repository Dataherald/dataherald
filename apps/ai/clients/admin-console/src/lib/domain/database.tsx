import { capitalize } from '@/lib/utils'
import { ETableSyncStatus, TableSyncStatus } from '@/models/api'
import { ColorClasses, ResourceColors } from '@/models/domain'
import {
  Check,
  CircleSlash,
  LucideIcon,
  RefreshCcw,
  ShieldAlert,
  XCircle,
} from 'lucide-react'

export const DOMAIN_TABLE_SYNC_STATUS_COLORS: ResourceColors<TableSyncStatus> =
  {
    [ETableSyncStatus.NOT_SCANNED]: {
      text: 'text-gray-500',
    },
    [ETableSyncStatus.SYNCHRONIZING]: {
      text: 'text-yellow-600',
    },
    [ETableSyncStatus.SCANNED]: {
      text: 'text-green-700',
    },
    [ETableSyncStatus.DEPRECATED]: {
      text: 'text-orange-800',
    },
    [ETableSyncStatus.FAILED]: {
      text: 'text-red-600',
    },
  }

export const formatDriver = (driver: string) => `${driver}://`

export const getDomainTableSyncStatusColors = (
  sync_status: TableSyncStatus,
): ColorClasses => {
  return DOMAIN_TABLE_SYNC_STATUS_COLORS[sync_status]
}

export const isSyncEnabled = (sync_status: TableSyncStatus): boolean =>
  [
    ETableSyncStatus.NOT_SCANNED,
    ETableSyncStatus.FAILED,
    ETableSyncStatus.SCANNED,
  ].includes(ETableSyncStatus[sync_status])

export const getDomainTableSyncStatusIcon = (
  sync_status: TableSyncStatus,
): LucideIcon | null => {
  switch (sync_status) {
    case ETableSyncStatus.SCANNED:
      return Check
    case ETableSyncStatus.SYNCHRONIZING:
      return RefreshCcw
    case ETableSyncStatus.NOT_SCANNED:
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
  return capitalize(sync_status?.replace('_', ' ').toLowerCase())
}

export const isDatabaseResource = (type?: string): boolean =>
  type === 'database'
export const isTableResource = (type?: string): boolean => type === 'table'
export const isColumnResource = (type?: string): boolean => type === 'column'
