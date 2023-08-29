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
  SQL_ERROR = 'SQL_ERROR',
  NOT_VERIFIED = 'NOT_VERIFIED',
  VERIFIED = 'VERIFIED',
}

export type QueryStatus = 'SQL_ERROR' | 'NOT_VERIFIED' | 'VERIFIED'

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
  nl_response: string
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
  nl_response: string
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

export interface Database {
  db_alias: string
  tables: {
    id?: string
    name: string
    columns: string[]
  }[]
}

export type Databases = Database[]
