const DATABASE_PROVIDERS = [
  {
    name: 'PostgreSQL',
    driver: 'postgresql+psycopg2',
    logoUrl: '/images/databases/postgresql.svg',
  },
  {
    name: 'MS SQL Server',
    driver: 'mssql+pymssql',
    logoUrl: '/images/databases/sql-server.svg',
  },
  {
    name: 'Databricks',
    driver: 'databricks',
    logoUrl: '/images/databases/databricks.svg',
  },
  {
    name: 'Snowflake',
    driver: 'snowflake',
    logoUrl: '/images/databases/snowflake.svg',
  },
  {
    name: 'BigQuery',
    driver: 'bigquery',
    logoUrl: '/images/databases/bigquery.svg',
  },
  {
    name: 'AWS Athena',
    driver: 'awsathena+rest',
    logoUrl: '/images/databases/aws-athena.svg',
  },
  {
    name: 'MariaDB',
    driver: 'mysql+pymysql',
    logoUrl: '/images/databases/mariadb.svg',
  },
  {
    name: 'ClickHouse',
    driver: 'clickhouse+http',
    logoUrl: '/images/databases/clickhouse.svg',
  },
]

export default DATABASE_PROVIDERS
