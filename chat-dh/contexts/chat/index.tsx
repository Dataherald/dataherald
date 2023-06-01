import { Messages } from '@/types/chat';
import { FC, ReactNode, createContext, useContext, useState } from 'react';

type SetMessagesFunction = (prevMessages: Messages) => Messages;
interface ChatContextType {
  messages: Messages;
  setMessages: (messages: Messages | SetMessagesFunction) => void;
  fetchingNewMessage: boolean;
  setFetchingNewMessage: (loadingNewMessage: boolean) => void;
  loadingIframe: boolean;
  setLoadingIframe: (loadingNewMessage: boolean) => void;
  loadingNewMessage: boolean;
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
  const [fetchingNewMessage, setFetchingNewMessage] = useState<boolean>(false);
  const [loadingIframe, setLoadingIframe] = useState<boolean>(false);

  const handleSetMessages = (messages: Messages | SetMessagesFunction) => {
    if (typeof messages === 'function') {
      setMessages((prevMessages) =>
        (messages as SetMessagesFunction)(prevMessages),
      );
    } else {
      setMessages(messages);
    }
  };

  const loadingNewMessage = fetchingNewMessage || loadingIframe;

  return (
    <ChatContext.Provider
      value={{
        messages,
        setMessages: handleSetMessages,
        fetchingNewMessage,
        setFetchingNewMessage,
        loadingIframe,
        setLoadingIframe,
        loadingNewMessage,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};
