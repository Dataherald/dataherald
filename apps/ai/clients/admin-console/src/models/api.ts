export interface User {
  slack_id?: string
  username: string
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
}

export type Queries = Query[]
