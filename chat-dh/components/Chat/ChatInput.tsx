import { Message } from "@/types";
import { FC, KeyboardEvent, useEffect, useRef, useState } from "react";
import { Icon } from "../Layout/Icon";

interface ChatInputProps {
  onSend: (message: Message) => void;
}

export const ChatInput: FC<ChatInputProps> = ({ onSend }) => {
  const [content, setContent] = useState<string>();

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length > 4000) {
      alert("Message limit is 4000 characters");
      return;
    }

    setContent(value);
  };

  const handleSend = () => {
    if (!content) {
      return;
    }
    onSend({ role: "user", content });
    setContent("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    if (textareaRef && textareaRef.current) {
      textareaRef.current.style.height = "inherit";
      textareaRef.current.style.minHeight = `${textareaRef.current?.scrollHeight}px`;
    }
  }, [content]);

  return (
    <div className="relative">
      <textarea
        ref={textareaRef}
        className="min-h-[44px] rounded-lg pl-4 pr-12 py-2 w-full focus:outline-none focus:ring-1 focus:ring-neutral-300 border border-black border-opacity-80"
        style={{ resize: "none" }}
        placeholder="Ask Dataherald a Real Estate prompt"
        value={content}
        rows={3}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
      />

      <button onClick={() => handleSend()}>
        <Icon
          value="send"
          type="filled"
          className="text-primary absolute right-2 bottom-3 h-8 w-8 hover:cursor-pointer rounded-full p-1 hover:opacity-80"
        />
      </button>
    </div>
  );
};
