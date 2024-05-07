import { DatabaseDialect, EDatabaseDialect } from '@/models/api'

export interface DatabaseProvider {
  name: string
  driver: string
  dialect: DatabaseDialect
  logoUrl: string
}

const DATABASE_PROVIDERS: DatabaseProvider[] = [
  {
    name: 'PostgreSQL',
    driver: 'postgresql+psycopg2',
    dialect: EDatabaseDialect.postgresql,
    logoUrl: '/images/databases/postgresql.svg',
  },
  {
    name: 'MS SQL Server',
    driver: 'mssql+pymssql',
    dialect: EDatabaseDialect.mssql,
    logoUrl: '/images/databases/sql-server.png',
  },
  {
    name: 'Databricks',
    driver: 'databricks',
    dialect: EDatabaseDialect.databricks,
    logoUrl: '/images/databases/databricks.svg',
  },
  {
    name: 'Snowflake',
    driver: 'snowflake',
    dialect: EDatabaseDialect.snowflake,
    logoUrl: '/images/databases/snowflake.svg',
  },
  {
    name: 'Redshift',
    driver: 'redshift+psycopg2',
    dialect: EDatabaseDialect.redshift,
    logoUrl: '/images/databases/redshift.png',
  },
  {
    name: 'BigQuery',
    driver: 'bigquery',
    dialect: EDatabaseDialect.bigquery,
    logoUrl: '/images/databases/bigquery.svg',
  },
  {
    name: 'AWS Athena',
    driver: 'awsathena+rest',
    dialect: EDatabaseDialect.awsathena,
    logoUrl: '/images/databases/aws-athena.svg',
  },
  {
    name: 'MariaDB',
    driver: 'mysql+pymysql',
    dialect: EDatabaseDialect.mysql,
    logoUrl: '/images/databases/mariadb.svg',
  },
  {
    name: 'ClickHouse',
    driver: 'clickhouse+http',
    dialect: EDatabaseDialect.clickhouse,
    logoUrl: '/images/databases/clickhouse.svg',
  },
]

export default DATABASE_PROVIDERS
