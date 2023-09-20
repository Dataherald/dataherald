import { UploadCloud } from 'lucide-react'
import Image from 'next/image'
import { FC } from 'react'
import { Button } from '../ui/button'

const dbProviders = [
  {
    src: '/images/databases/postgresql.svg',
    name: 'PostgreSQL',
    alt: 'Postgresql logo',
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

const DatabaseConnection: FC = () => {
  return (
    <div className="grow flex flex-col items-center justify-center gap-16">
      <div className="grid grid-cols-5 gap-12">
        {dbProviders.map(({ src, name, alt }, idx) => (
          <div key={idx} className="flex flex-col items-center gap-3">
            <Image
              className="grow"
              priority
              src={src}
              alt={alt}
              width={96}
              height={96}
              style={{ objectFit: 'contain' }}
            />
            <span>{name}</span>
          </div>
        ))}
      </div>
      <Button size="lg">
        <UploadCloud className="mr-2" />
        Connect your Database
      </Button>
    </div>
  )
}

export default DatabaseConnection
