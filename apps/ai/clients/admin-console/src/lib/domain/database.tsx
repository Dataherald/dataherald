import { ESchemaStatus, SchemaStatus } from '@/models/api'
import { EDomainSchemaStatusTextColor } from '@/models/domain'
import {
  Check,
  CircleSlash,
  LucideIcon,
  RefreshCcw,
  ShieldAlert,
  XCircle,
} from 'lucide-react'

export const formatDriver = (driver: string) => `${driver}://`

export const getDomainSchemaStatusColor = (
  status: SchemaStatus,
): EDomainSchemaStatusTextColor => {
  return EDomainSchemaStatusTextColor[status]
}

export const isSelectableByStatus = (status: SchemaStatus): boolean =>
  [
    ESchemaStatus.NOT_SYNCHRONIZED,
    ESchemaStatus.FAILED,
    ESchemaStatus.SYNCHRONIZED,
  ].includes(ESchemaStatus[status])

export const getDomainSchemaStatusIcon = (
  status: SchemaStatus,
): LucideIcon | null => {
  switch (status) {
    case ESchemaStatus.SYNCHRONIZED:
      return Check
    case ESchemaStatus.SYNCHRONIZING:
      return RefreshCcw
    case ESchemaStatus.NOT_SYNCHRONIZED:
      return CircleSlash
    case ESchemaStatus.DEPRECATED:
      return ShieldAlert
    case ESchemaStatus.FAILED:
      return XCircle
    default:
      return null
  }
}

export const formatSchemaStatus = (status: SchemaStatus): string => {
  return status?.replace('_', ' ').toLowerCase()
}
