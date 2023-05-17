import { useChat } from '@/context/chat';
import { usePrompt } from '@/context/prompt';
import analyticsService from '@/services/analytics';
import apiService from '@/services/api';
import { Message, MessageContent } from '@/types/chat';
import { isAbortError } from '@/utils/api';
import { useUser } from '@auth0/nextjs-auth0/client';
import { FC, useCallback, useEffect, useLayoutEffect, useRef } from 'react';
import Button from '../Layout/Button';
import { Header } from '../Layout/Header';
import { ChatInput } from './ChatInput';
import { ChatKickoff } from './ChatKickoff';
import { ChatMessage } from './ChatMessage';

export const Chat: FC = () => {
  const { messages, setMessages, loading, setLoading, error } = useChat();
  const { user } = useUser();
  const { prompt, setPrompt } = usePrompt();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatAbortControllerRef = useRef<AbortController | null>();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = useCallback(
    async (newUserMessage: string) => {
      const newMessage: Message = {
        role: 'user',
        content: newUserMessage,
      };
      const updatedMessages: Message[] = [...messages, newMessage];
      const abortController = new AbortController();
      chatAbortControllerRef.current = abortController;
      setLoading(true);
      setMessages([
        ...updatedMessages,
        {
          role: 'assistant',
          content: {
            status: 'loading',
          },
        },
      ]);
      try {
        const chatResponse = await apiService.chat(
          updatedMessages,
          user?.email || '',
          chatAbortControllerRef.current?.signal,
        );
        analyticsService.track('new-user-prompt', {
          prompt: newUserMessage,
          status: 'success',
        });
        setMessages((prevMessages) =>
          prevMessages.map((message) =>
            (message.content as MessageContent).status === 'loading'
              ? {
                  role: 'assistant',
                  content: chatResponse,
                }
              : message,
          ),
        );
      } catch (e) {
        let messageText: string;
        if (isAbortError(e)) {
          messageText = 'User has cancelled the request.';
          analyticsService.track('new-user-prompt', {
            prompt: newUserMessage,
            status: 'canceled',
          });
        } else {
          messageText = 'Something went wrong. Please try again later.';
          analyticsService.track('new-user-prompt', {
            prompt: newUserMessage,
            status: 'error',
          });
        }
        setMessages((prevMessages) =>
          prevMessages.map((message) =>
            (message.content as MessageContent).status === 'loading'
              ? {
                  role: 'assistant',
                  content: {
                    status: 'error',
                    generated_text: messageText,
                  },
                }
              : message,
          ),
        );
      } finally {
        setLoading(false);
      }
    },
    [messages, setMessages, setLoading, user],
  );

  const handleExample = useCallback(
    (prompt: string) => {
      sendMessage(prompt);
    },
    [sendMessage],
  );

  const handleReset = useCallback(() => {
    setMessages([]);
  }, [setMessages]);

  const handleAbort = () => {
    if (chatAbortControllerRef.current) chatAbortControllerRef.current.abort();
  };

  useLayoutEffect(() => {
    scrollToBottom();
  }, [messages, loading, error]);

  useEffect(() => {
    if (prompt) {
      handleExample(prompt);
      setPrompt(null);
    }
  }, [prompt, setPrompt, handleExample]);

  return (
    <>
      {!messages.length ? (
        <div className="flex-1 flex flex-col gap-2 py-6 px-4 w-full max-w-[1000px] mx-auto">
          <Header title="Dataherald AI - Technical preview"></Header>
          <div className="flex-grow">
            <ChatKickoff onExampleClick={handleExample}></ChatKickoff>
          </div>
          <div className="mt-4">
            <ChatInput onSend={sendMessage} />
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col mb-4">
          <div className="flex flex-col flex-grow">
            {messages.map((message, index) => (
              <ChatMessage
                key={index}
                message={message}
                scrollToBottom={scrollToBottom}
              />
            ))}
          </div>
          <div className="flex flex-col gap-4 items-center px-4">
            {loading ? (
              <Button
                color="primary-light"
                icon="stop"
                className="hover:bg-gray-200 text-secondary-dark"
                onClick={handleAbort}
              >
                Stop Generating
              </Button>
            ) : (
              <Button
                color="primary-light"
                icon="message"
                className="hover:bg-gray-200 text-secondary-dark"
                onClick={handleReset}
              >
                New Chat
              </Button>
            )}

            <div className="w-full max-w-[1000px] mx-auto">
              <ChatInput onSend={sendMessage} />
            </div>
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </>
  );
};
