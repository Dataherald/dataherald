export interface User {
  id: string
  name: string
}

export enum EQueryStatus {
  SQL_ERROR = 'SQL_ERROR',
  NOT_VERIFIED = 'NOT_VERIFIED',
  VERIFIED = 'VERIFIED',
}

export type QueryStatus = 'SQL_ERROR' | 'NOT_VERIFIED' | 'VERIFIED'

export type QuerySqlResult = {
  columns: string[]
  rows: { [columnKey: string]: string | number }[]
}

export interface Query {
  id: string
  question: string
  question_date: string
  sql_query: string
  sql_query_result: QuerySqlResult
  ai_process: string[]
  nl_response: string
  status: QueryStatus
  evaluation_score: number
  user: User
  last_updated: string
}

export type Queries = Query[]
