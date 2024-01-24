import DatabaseConnectionFormDialog from '@/components/databases/database-connection-form-dialog'
import DATABASE_PROVIDERS from '@/constants/database-providers'
import Image from 'next/image'
import { FC } from 'react'

const DatabaseConnection: FC<{
  onConnected: () => void
  onFinish: () => void
}> = ({ onConnected, onFinish }) => (
  <div className="grow flex flex-col items-center justify-center gap-16">
    <div className="grid grid-cols-5 gap-12">
      {DATABASE_PROVIDERS.map(({ logoUrl, name }, idx) => (
        <div key={idx} className="flex flex-col items-center gap-3">
          <Image
            className="grow"
            priority
            src={logoUrl}
            alt={`${name} Logo`}
            width={96}
            height={96}
            style={{ width: 96, height: 96, objectFit: 'contain' }}
          />
          <span>{name}</span>
        </div>
      ))}
    </div>
    <DatabaseConnectionFormDialog
      isFirstConnection
      onConnected={onConnected}
      onFinish={onFinish}
    />
  </div>
)

export default DatabaseConnection
