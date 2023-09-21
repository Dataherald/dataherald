const DATABASE_PROVIDERS = [
  {
    name: 'PostgreSQL',
    driver: 'postgresql+psycopg2',
    logoUrl: '/images/databases/postgresql.svg',
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
]

export default DATABASE_PROVIDERS
