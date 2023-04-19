export type Role = "assistant" | "user";
export interface Message {
  role: Role;
  content: string | ChatResponse;
}

export interface ChatResponse {
  id: string;
  generated_text: string;
  viz_id: string;
}

// Unused
export enum OpenAIModel {
  DAVINCI_TURBO = "gpt-3.5-turbo",
}
