import { MaterialIcon } from "material-icons";

export type MenuItem = {
  label: string;
  href: string;
  icon?: MaterialIcon;
};

export type MenuItems = MenuItem[];

export enum OpenAIModel {
  DAVINCI_TURBO = "gpt-3.5-turbo",
}

export interface Message {
  role: Role;
  content: string;
}

export type Role = "assistant" | "user";
