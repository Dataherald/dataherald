import { Message } from "@/types/chat";
import { FC, KeyboardEvent, useRef, useState } from "react";
import { Icon } from "../Layout/Icon";

interface ChatInputProps {
  disabled?: boolean;
  onSend: (message: Message) => void;
}

const VALIDATIONS = {
  MAX_CHARACTERS: 1000,
};

export const ChatInput: FC<ChatInputProps> = ({ disabled = false, onSend }) => {
  const [content, setContent] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setContent(value);

    if (value.length > VALIDATIONS.MAX_CHARACTERS) {
      setError(`Message limit is ${VALIDATIONS.MAX_CHARACTERS} characters`);
    } else {
      setError(null);
    }
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
      if (!error) handleSend();
    }
  };

  return (
    <div className="relative">
      <textarea
        ref={textareaRef}
        className={`min-h-[44px] rounded-lg pl-4 pr-12 py-2 w-full focus:outline-none focus:ring-1 focus:ring-neutral-300 border border-black border-opacity-80 ${
          disabled && "opacity-80"
        } ${error && "border-yellow-600 text-yellow-600"}`}
        style={{ resize: "none" }}
        placeholder={
          disabled
            ? "Only one message at a time is supported"
            : "Ask Dataherald a Real Estate prompt"
        }
        value={content}
        rows={3}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        disabled={disabled}
      />
      <button onClick={() => handleSend()} disabled={disabled || !!error}>
        <Icon
          value="send"
          type="filled"
          className={`text-secondary-dark absolute right-2 h-8 w-8 rounded-full p-1 ${
            disabled || !!error
              ? "opacity-50"
              : "hover:opacity-80 hover:cursor-pointer"
          } ${error ? "bottom-[4rem]" : "bottom-[2.3rem]"}`}
        />
      </button>
      {error && (
        <div className="text-yellow-600 mt-2 pl-4 text-sm">{error}</div>
      )}
    </div>
  );
};
