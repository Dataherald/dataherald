import DatabaseConnectionFormDialog from '@/components/databases/database-connection-form-dialog'
import { ContentBox } from '@/components/ui/content-box'
import DATABASE_PROVIDERS from '@/constants/database-providers'
import Image from 'next/image'
import { FC } from 'react'

const DB_LOGO_SIZE = 45

const FirstDatabaseConnection: FC<{
  onConnected: () => void
  onFinish: () => void
}> = ({ onConnected, onFinish }) => (
  <ContentBox className="m-6 flex flex-col items-center justify-center gap-8">
    <h1 className="text-xl font-bold">
      Connect your first database to get started
    </h1>
    <DatabaseConnectionFormDialog
      isFirstConnection
      onConnected={onConnected}
      onFinish={onFinish}
    />
    <div className="flex flex-wrap max-w-md items-center justify-center gap-12">
      {DATABASE_PROVIDERS.map(({ logoUrl, name }, idx) => (
        <div key={idx} className="flex flex-col items-center gap-3">
          <Image
            className="grow"
            priority
            src={logoUrl}
            alt={`${name} Logo`}
            width={DB_LOGO_SIZE}
            height={DB_LOGO_SIZE}
            style={{
              width: DB_LOGO_SIZE,
              height: DB_LOGO_SIZE,
              objectFit: 'contain',
            }}
          />
          <span className="tracking-wide text-slate-800 text-xs">{name}</span>
        </div>
      ))}
    </div>
  </ContentBox>
)

export default FirstDatabaseConnection
