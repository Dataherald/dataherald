export type ResponseStatus = 'successful' | 'failed' | 'error' | 'loading';

export interface ChatResponse {
  id: string;
  status: ResponseStatus;
  user: null;
  date_entered: string;
  message: string;
  generated_text: string;
  viz_id: string | null;
}

export interface ChatErrorResponse {
  code: string;
  generated_text: string;
  status: ResponseStatus;
}
