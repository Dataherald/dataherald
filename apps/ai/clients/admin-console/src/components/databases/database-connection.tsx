import DatabaseConnectionDialog from '@/components/databases/database-connection-dialog'
import Image from 'next/image'
import { FC } from 'react'

const DB_PROVIDERS = [
  {
    src: '/images/databases/postgresql.svg',
    name: 'PostgreSQL',
    alt: 'PostgreSQL logo',
  },
  {
    src: '/images/databases/bigquery.svg',
    name: 'BigQuery',
    alt: 'Bigquery logo',
  },
  {
    src: '/images/databases/snowflake.svg',
    name: 'Snowflake',
    alt: 'Snowflake logo',
  },
  {
    src: '/images/databases/databricks.svg',
    name: 'Databricks',
    alt: 'Databricks logo',
  },
  {
    src: '/images/databases/aws-athena.svg',
    name: 'AWS Athena',
    alt: 'AWS Athena logo',
  },
]

const DatabaseConnection: FC<{
  onConnected: () => void
  onFinish: () => void
}> = ({ onConnected, onFinish }) => (
  <div className="grow flex flex-col items-center justify-center gap-16">
    <div className="grid grid-cols-5 gap-12">
      {DB_PROVIDERS.map(({ src, name, alt }, idx) => (
        <div key={idx} className="flex flex-col items-center gap-3">
          <Image
            className="grow"
            priority
            src={src}
            alt={alt}
            width={96}
            height={96}
            style={{ width: 96, height: 96, objectFit: 'contain' }}
          />
          <span>{name}</span>
        </div>
      ))}
    </div>
    <DatabaseConnectionDialog
      onConnected={() => onConnected()}
      onFinish={() => onFinish()}
    />
  </div>
)

export default DatabaseConnection
