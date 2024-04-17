import { SelectOption } from '@/components/ui/select'
import DATABASE_PROVIDERS, {
  DatabaseProvider,
} from '@/constants/database-providers'
import { Database } from 'lucide-react'
import Image from 'next/image'
import { useMemo } from 'react'

export type DBConnectionOptionData = {
  id: string
  alias?: string
  dialect: string
}

const useDatabaseOptions = (
  databaseConnections: DBConnectionOptionData[] = [],
): SelectOption[] =>
  useMemo(
    () =>
      databaseConnections.map(({ id, alias, dialect }) => {
        const provider: DatabaseProvider | undefined = DATABASE_PROVIDERS.find(
          (provider) => provider.dialect === dialect,
        )
        const dbLogo: JSX.Element =
          provider && provider.logoUrl ? (
            <Image
              priority
              src={provider.logoUrl}
              alt={`${alias || id} logo`}
              width={18}
              height={18}
            />
          ) : (
            <Database size={16} />
          )

        return {
          label: alias || id,
          value: id,
          icon: dbLogo,
        }
      }),
    [databaseConnections],
  )

export default useDatabaseOptions
