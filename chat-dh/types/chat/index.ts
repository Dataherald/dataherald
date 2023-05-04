import { ResponseStatus } from "../api";

export type Role = "assistant" | "user";

export interface MessageContent {
  status: ResponseStatus;
  generated_text?: string;
  id?: string; // ChatResponse id
  viz_id?: string | null;
}
export type Messages = Message[];
export interface Message {
  role: Role;
  content: string | MessageContent;
}

// Unused
export enum OpenAIModel {
  DAVINCI_TURBO = "gpt-3.5-turbo",
}
