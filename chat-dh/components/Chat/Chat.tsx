import { Message } from "@/types/chat";
import { FC } from "react";
import { ChatInput } from "./ChatInput";
import { ChatLoader } from "./ChatLoader";
import { ChatMessage } from "./ChatMessage";

interface ChatProps {
  messages: Message[];
  loading: boolean;
  onSend: (message: Message) => void;
}

export const Chat: FC<ChatProps> = ({ messages, loading, onSend }) => {
  return (
    <div className="flex flex-col flex-1">
      <div className="flex flex-col flex-grow">
        {messages.map((message, index) => (
          <div key={index} className="my-4">
            <ChatMessage message={message} />
          </div>
        ))}
        {loading && (
          <div className="my-4">
            <ChatLoader />
          </div>
        )}
      </div>
      <div className="mt-4">
        <ChatInput onSend={onSend} />
      </div>
    </div>
  );
};
