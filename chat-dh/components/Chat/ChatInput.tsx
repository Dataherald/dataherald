import { useChat } from '@/context/chat';
import { FC, KeyboardEvent, useRef, useState } from 'react';
import { Icon } from '../Layout/Icon';

const VALIDATIONS = {
  MAX_CHARACTERS: 1000,
};

interface ChatInputProps {
  onSend: (content: string) => void;
}

export const ChatInput: FC<ChatInputProps> = ({ onSend }) => {
  const [content, setContent] = useState<string>('');
  const { error, setError, loading, messages } = useChat();
  const emptyMessages = messages.length === 0;

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

  const handleSendUserMessage = () => {
    if (!content) {
      return;
    }
    onSend(content);
    setContent('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!error) handleSendUserMessage();
    }
  };

  return (
    <div className="relative max-w-[1000px] mx-auto">
      <textarea
        ref={textareaRef}
        className={`min-h-[44px] rounded-lg pl-4 pr-12 py-2 w-full focus:outline-none focus:ring-1 focus:ring-neutral-300 border border-black border-opacity-20 shadow-[0px_0px_40px_4px_rgba(0,0,0,0.10)] ${
          loading && 'opacity-80'
        } ${error && 'border-yellow-600 text-yellow-600'}`}
        style={{ resize: 'none' }}
        placeholder={
          loading
            ? 'Only one message at a time is supported'
            : emptyMessages
            ? 'Ask Dataherald a Real Estate prompt'
            : 'We don’t support for chat history context yet, but we will soon. Ask Dataherald another Real Estate prompt...'
        }
        value={content}
        rows={3}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        disabled={loading}
      />
      <button onClick={handleSendUserMessage} disabled={loading || !!error}>
        <Icon
          value="send"
          type="filled"
          className={`text-secondary-dark absolute right-2 h-8 w-8 rounded-full p-1 ${
            loading || !!error
              ? 'opacity-50'
              : 'hover:opacity-80 hover:cursor-pointer'
          } ${error ? 'bottom-[4rem]' : 'bottom-[2.3rem]'}`}
        />
      </button>
      {error && (
        <div className="text-yellow-600 mt-2 pl-4 text-sm">{error}</div>
      )}
    </div>
  );
};
