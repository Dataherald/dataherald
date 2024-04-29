import { UserProfile } from '@auth0/nextjs-auth0/client'

export interface ErrorResponse {
  message: string
  error_code: string
  trace_id?: string
  description?: string
  detail?: Record<string, string>
}

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

export interface SlackConfig {
  slack_installation: SlackInstallation
  db_connection_id: string
}

export enum EPaymentPlan {
  CREDIT_ONLY = 'CREDIT_ONLY',
  USAGE_BASED = 'USAGE_BASED',
  ENTERPRISE = 'ENTERPRISE',
}

export type PaymentPlan = keyof typeof EPaymentPlan

export interface InvoiceDetails {
  plan: PaymentPlan
  billing_cycle_anchor?: number
  spending_limit?: number // in cents
  available_credits?: number // in cents
  stripe_customer_id?: string
  stripe_subscription_id?: string
}

export interface Organization {
  id: string
  name: string
  confidence_threshold: number
  llm_api_key?: string
  slack_config?: SlackConfig
  invoice_details: InvoiceDetails
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
  created_at: string
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

export enum EGenerationSource {
  API = 'API',
  SLACK = 'SLACK',
  PLAYGROUND = 'PLAYGROUND',
  QUERY_EDITOR_RUN = 'QUERY_EDITOR_RUN',
  QUERY_EDITOR_RESUBMIT = 'QUERY_EDITOR_RESUBMIT',
}

export type GenerationSource = keyof typeof EGenerationSource

export enum EQuerySource {
  API = 'API',
  SLACK = 'SLACK',
  PLAYGROUND = 'PLAYGROUND',
}

export type QuerySource = keyof typeof EQuerySource

export type QuerySqlResult = {
  columns?: string[]
  rows?: QuerySqlResultData[]
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
  db_connection_id: string
  db_connection_alias: string
  slack_message_last_sent_at: string | null
  source: QuerySource
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
  db_connection_alias: string
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
  slack_message_last_sent_at: string | null
  source: QuerySource
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
  db_connection_alias: string
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
  QUEUING_FOR_SCAN = 'QUEUING_FOR_SCAN', // front-end only
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

export interface BasicTableDescription {
  id: string
  name: string
  schema_name?: string
  columns: string[]
  sync_status: TableSyncStatus
  last_sync: string | null
}

export interface DatabaseSchema {
  name: string
  tables: BasicTableDescription[]
}

export interface Database {
  db_connection_id: string
  db_connection_alias: string
  dialect?: DatabaseDialect
  schemas?: string[]
  tables: BasicTableDescription[]
}

export type Databases = Database[]

export interface SshSettings {
  host: string
  port: string
  username: string
  password: string
}

export enum EDatabaseDialect {
  postgresql = 'postgresql',
  mysql = 'mysql',
  mssql = 'mssql',
  databricks = 'databricks',
  snowflake = 'snowflake',
  redshift = 'redshift',
  clickhouse = 'clickhouse',
  awsathena = 'awsathena',
  duckdb = 'duckdb',
  bigquery = 'bigquery',
  sqlite = 'sqlite',
}

export type DatabaseDialect = keyof typeof EDatabaseDialect

export const SCHEMA_SUPPORTED_DIALECTS: Set<DatabaseDialect> = new Set([
  EDatabaseDialect.bigquery,
  EDatabaseDialect.snowflake,
  EDatabaseDialect.databricks,
  EDatabaseDialect.postgresql,
])

export interface DatabaseConnection {
  id?: string
  alias: string
  use_ssh: boolean
  connection_uri: string
  schemas?: string[]
  ssh_settings?: SshSettings
  dialect?: DatabaseDialect
}

export type DatabaseConnections = DatabaseConnection[]

export interface SampleDatabaseConnection {
  id: string
  alias: string
  description: string
  example_prompts: string[]
  dialect: DatabaseDialect
}

export type SampleDatabaseConnections = SampleDatabaseConnection[]

export enum EFineTuningStatus {
  QUEUED = 'queued',
  RUNNING = 'running',
  SUCCEEDED = 'succeeded',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  VALIDATING_FILES = 'validating_files',
}

export type FineTuningStatus = keyof typeof EFineTuningStatus

export interface BaseLLM {
  model_provider?: string | null
  model_name: string | null
  model_parameters: Record<string, string> | null
}

export interface DHFinetuningMetadata {
  organization_id: string | null
}

export interface FinetuningMetadata {
  dh_internal: DHFinetuningMetadata | null
  [key: string]: unknown
}

export interface FineTuningModel {
  id: string
  status: FineTuningStatus
  alias?: string
  db_connection_id?: string
  db_connection_alias?: string
  error?: string
  base_llm?: BaseLLM
  finetuning_file_id?: string
  finetuning_job_id?: string
  model_id?: string
  created_at?: string
  golden_records?: string[]
  metadata?: FinetuningMetadata
}

export type FineTuningModels = FineTuningModel[]

export interface ApiKey {
  id: string
  name: string
  organization_id: string
  created_at: string
  key_preview: string
  api_key?: string
}

export type ApiKeys = ApiKey[]

export type Usage = {
  available_credits: number
  total_credits: number
  amount_due: number
  spending_limit: number
  sql_generation_cost: number
  finetuning_gpt_35_cost: number
  finetuning_gpt_4_cost: number
  current_period_start?: string
  current_period_end?: string
}

export type SpendingLimits = {
  spending_limit: number
  hard_spending_limit: number
}

export type CreditCardBrand =
  | 'amex'
  | 'diners'
  | 'discover'
  | 'eftpos_au'
  | 'jcb'
  | 'mastercard'
  | 'unionpay'
  | 'visa'
  | 'unknown'

export type PaymentMethod = {
  id: string
  funding: 'credit' | 'debit' | 'prepaid' | 'unknown'
  brand: CreditCardBrand
  last4: string
  exp_month: number
  exp_year: number
  is_default: boolean
  provider_name: string
}

export type PaymentMethods = PaymentMethod[]
