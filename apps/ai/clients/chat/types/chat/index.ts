import { ResponseStatus } from '../api';

export type Role = 'assistant' | 'user';
export type MessageStatus = ResponseStatus | 'error' | 'loading' | 'canceled';
export type MessageLoadingStage =
  | 'viz_id'
  | 'generated_text'
  | 'json_object'
  | 'none';

export interface MessageContent {
  status: MessageStatus;
  message?: string;
  generated_text?: string;
  viz_id?: string | null;
  id?: string; // ChatResponse id
}
export type Messages = Message[];
export interface Message {
  role: Role;
  content: string | MessageContent;
}

// Unused
export enum OpenAIModel {
  DAVINCI_TURBO = 'gpt-3.5-turbo',
}
