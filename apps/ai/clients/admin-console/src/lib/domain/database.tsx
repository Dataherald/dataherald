import DATABASE_PROVIDERS, {
  DatabaseProvider,
} from '@/constants/database-providers'
import { capitalizeFirstLetter } from '@/lib/utils'
import {
  DatabaseDialect,
  ETableSyncStatus,
  SCHEMA_SUPPORTED_DIALECTS,
  TableSyncStatus,
} from '@/models/api'
import { ColorClasses, ResourceColors } from '@/models/domain'
import {
  Check,
  CircleSlash,
  Database,
  Loader,
  LucideIcon,
  RefreshCcw,
  ShieldAlert,
  XCircle,
} from 'lucide-react'
import Image from 'next/image'

export const DOMAIN_TABLE_SYNC_STATUS_COLORS: ResourceColors<TableSyncStatus> =
  {
    [ETableSyncStatus.NOT_SCANNED]: {
      text: 'text-slate-500',
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
    [ETableSyncStatus.QUEUING_FOR_SCAN]: {
      text: 'text-slate-700',
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
    case ETableSyncStatus.QUEUING_FOR_SCAN:
      return Loader
    default:
      return null
  }
}

export const formatTableSyncStatus = (sync_status: TableSyncStatus): string => {
  const text = sync_status === 'SYNCHRONIZING' ? 'scanning' : sync_status
  return capitalizeFirstLetter(text.replace(/_/g, ' ').toLowerCase())
}

export const isDatabaseResource = (type?: string): boolean =>
  type === 'database'
export const isTableResource = (type?: string): boolean => type === 'table'
export const isColumnResource = (type?: string): boolean => type === 'column'

export const supportsSchemas = (
  dialect?: DatabaseDialect,
): boolean | undefined => dialect && SCHEMA_SUPPORTED_DIALECTS.has(dialect)

export const getDatabaseLogo = (database: {
  id: string
  alias?: string
  dialect?: DatabaseDialect
}): JSX.Element => {
  const provider: DatabaseProvider | undefined = DATABASE_PROVIDERS.find(
    (provider) => provider.dialect === database.dialect,
  )
  return provider && provider.logoUrl ? (
    <Image
      priority
      src={provider.logoUrl}
      alt={`${database.alias || database.id} logo`}
      width={18}
      height={18}
    />
  ) : (
    <Database size={16} />
  )
}
