import { ChatResponse } from "../api";

export type Role = "assistant" | "user";
export interface Message {
  role: Role;
  content: string | ChatResponse;
}

// Unused
export enum OpenAIModel {
  DAVINCI_TURBO = "gpt-3.5-turbo",
}
