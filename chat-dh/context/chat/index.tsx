import { Messages } from '@/types/chat';
import { FC, ReactNode, createContext, useContext, useState } from 'react';

type SetMessagesFunction = (prevMessages: Messages) => Messages;
interface ChatContextType {
  messages: Messages;
  setMessages: (messages: Messages | SetMessagesFunction) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
  iframeLoading: boolean;
  setIframeLoading: (loadiingIframe: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviverProps {
  children: ReactNode;
}

export const ChatProvider: FC<ChatProviverProps> = ({ children }) => {
  const [messages, setMessages] = useState<Messages>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [iframeLoading, setIframeLoading] = useState<boolean>(false);

  const handleSetMessages = (messages: Messages | SetMessagesFunction) => {
    if (typeof messages === 'function') {
      setMessages((prevMessages) =>
        (messages as SetMessagesFunction)(prevMessages),
      );
    } else {
      setMessages(messages);
    }
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        setMessages: handleSetMessages,
        loading,
        setLoading,
        iframeLoading,
        setIframeLoading,
        error,
        setError,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};
