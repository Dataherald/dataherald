import { SelectOption } from '@/components/ui/select'
import { getDatabaseLogo } from '@/lib/domain/database'
import { DatabaseDialect } from '@/models/api'
import { useMemo } from 'react'

export type DBConnectionOptionData = {
  id: string
  alias?: string
  dialect: DatabaseDialect
}

const useDatabaseOptions = (
  databaseConnections: DBConnectionOptionData[] = [],
): SelectOption[] =>
  useMemo(
    () =>
      databaseConnections.map((db) => ({
        label: db.alias || db.id,
        value: db.id,
        icon: getDatabaseLogo(db),
      })),
    [databaseConnections],
  )

export default useDatabaseOptions
