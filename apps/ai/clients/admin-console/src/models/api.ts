import { UserProfile } from '@auth0/nextjs-auth0/client'

export interface SlackTeam {
  id: string | null
  name: string | null
}
export interface SlackUser {
  token: string | null
  scopes: string | null
  id: string | null
}
export interface SlackBot {
  scopes: string[] | null
  token: string | null
  user_id: string | null
  id: string | null
}
export interface SlackInstallation {
  team: SlackTeam | null
  enterprise: string | null
  user: SlackUser | null
  token_type: string | null
  is_enterprise_install: boolean | null
  app_id: string | null
  auth_version: string | null
  bot: SlackBot | null
}

export interface Organization {
  id: string
  name: string
  confidence_threshold: number
  db_connection_id?: string
  llm_api_key?: string
  slack_installation?: SlackInstallation
}

export type Organizations = Organization[]

export enum ERole {
  ADMIN = 'ADMIN',
}

export type Roles = keyof typeof ERole

export interface User extends UserProfile {
  id: string
  organization_id: string
  role: Roles | null
}

export type Users = User[]

export enum EQueryStatus {
  INITIALIZED = 'INITIALIZED',
  REJECTED = 'REJECTED',
  ERROR = 'ERROR',
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
  created_by: string
  prompt_text: string
  nl_generation_text: string
  status: QueryStatus
  confidence_score: number
  display_id: string
  created_at: string
}

export type QueryList = QueryListItem[]

export type SlackInfo = {
  user_id: string
  channel_id: string
  thread_ts: string
  username: string
}

export interface Query {
  // prompt
  id: string
  db_connection_id: string
  prompt_text: string
  created_by: string
  updated_by: string
  organization_id: string
  display_id: string
  slack_info: SlackInfo
  message: string | null
  // sql_generation
  sql: string
  sql_result: QuerySqlResult | null // TODO remove this field once csv export is done
  sql_generation_error?: string
  confidence_score: number
  intermediate_steps: string[] | [] // TODO remove this field @valak

  // nl_generation
  nl_generation_text: string // TODO remove this field once the backend migrated to `message`

  status: QueryStatus
  updated_at: string
  created_at: string
}

export type Queries = Query[]

export enum EGoldenSqlSource {
  USER_UPLOAD = 'USER_UPLOAD',
  VERIFIED_QUERY = 'VERIFIED_QUERY',
}

export type GoldenSqlSource = 'USER_UPLOAD' | 'VERIFIED_QUERY'

export type DHGoldenSqlMetadata = {
  prompt_id: string
  organization_id: string
  source: GoldenSqlSource
  display_id: string
}

export type GoldenSqlMetadata = {
  dh_internal: DHGoldenSqlMetadata
}

export interface GoldenSqlListItem {
  id: string
  db_connection_id: string
  prompt_text: string
  sql: string
  created_at: string
  metadata: GoldenSqlMetadata
}

export type GoldenSqlList = GoldenSqlListItem[]

export enum ETableSyncStatus {
  NOT_SCANNED = 'NOT_SCANNED',
  SYNCHRONIZING = 'SYNCHRONIZING',
  SCANNED = 'SCANNED',
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
