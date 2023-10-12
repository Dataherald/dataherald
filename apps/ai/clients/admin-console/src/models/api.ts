import { UserProfile } from '@auth0/nextjs-auth0/client'

export interface Organization {
  id: string
  name: string
  slack_workspace_id: string
}

// TODO temoporary class
export interface AuthUser extends UserProfile {
  slack_id?: string
  organization_name: string
}

export interface User extends UserProfile {
  slack_id?: string
  organization: Organization
}

export enum EQueryStatus {
  REJECTED = 'REJECTED',
  SQL_ERROR = 'SQL_ERROR',
  NOT_VERIFIED = 'NOT_VERIFIED',
  VERIFIED = 'VERIFIED',
}

export type QueryStatus = keyof typeof EQueryStatus

export type QuerySqlResult = {
  columns: string[]
  rows: QuerySqlResultData[]
}

export type QuerySqlResultData = { [columnKey: string]: string | number }

export interface QueryListItem {
  id: string
  display_id: string
  username: string
  question: string
  question_date: string
  response: string
  status: QueryStatus
  evaluation_score: number
}

export type QueryList = QueryListItem[]

export interface Query {
  id: string
  question: string
  question_date: string
  sql_query: string
  sql_query_result: QuerySqlResult | null
  sql_error_message?: string
  ai_process: string[]
  response: string
  status: QueryStatus
  evaluation_score: number
  username: string
  last_updated: string
  updated_by: User
  verified_date: string
}

export type Queries = Query[]

export enum EGoldenSqlSource {
  USER_UPLOAD = 'USER_UPLOAD',
  VERIFIED_QUERY = 'VERIFIED_QUERY',
}

export type GoldenSqlSource = 'USER_UPLOAD' | 'VERIFIED_QUERY'

export interface GoldenSqlListItem {
  id: string
  display_id: string
  question: string
  sql_query: string
  created_time: string
  source: GoldenSqlSource
  verified_query_id?: string | null
  verified_query_display_id?: string | null
}

export type GoldenSqlList = GoldenSqlListItem[]

export enum ETableSyncStatus {
  NOT_SYNCHRONIZED = 'NOT_SYNCHRONIZED',
  SYNCHRONIZING = 'SYNCHRONIZING',
  SYNCHRONIZED = 'SYNCHRONIZED',
  DEPRECATED = 'DEPRECATED',
  FAILED = 'FAILED',
}

export type TableSyncStatus = keyof typeof ETableSyncStatus

export type TableDescription = {
  id: string
  table_name: string
  description: string | null
  status: TableSyncStatus
  last_schema_sync: string
  columns: ColumnDescription[]
}

export type Instruction = {
  id: string
  instruction: string
  db_connection_id: string
}

export type ColumnDescription = {
  name: string
  description: string | null
  is_primary_key: boolean
  data_type: string
  low_cardinality: boolean
  categories: string[]
}

export interface Database {
  db_connection_id: string
  alias: string
  tables: {
    id: string
    name: string
    columns: string[]
    sync_status: TableSyncStatus
    last_sync: string | null
  }[]
}

export type Databases = Database[]

export interface SshSettings {
  db_driver: string
  db_name: string
  host: string
  username: string
  password: string
  remote_host: string
  remote_db_name: string
  remote_db_password: string
  private_key_password?: string
}

export interface DatabaseConnection {
  alias: string
  use_ssh: boolean
  connection_uri?: string
  ssh_settings?: SshSettings
}
