export interface User {
  id: string | number // TODO remove number
  name: string
}

export enum EQueryStatus {
  SQL_ERROR = 'SQL_ERROR',
  NOT_VERIFIED = 'NOT_VERIFIED',
  VERIFIED = 'VERIFIED',
}

export type QueryStatus = 'SQL_ERROR' | 'NOT_VERIFIED' | 'VERIFIED'

export interface Query {
  id: string
  user: User
  question: string
  nl_response: string
  sql_query: string
  question_date: string
  ai_process: string
  last_updated: string
  status: QueryStatus
  evaluation_score: number
}

export type Queries = Query[]
