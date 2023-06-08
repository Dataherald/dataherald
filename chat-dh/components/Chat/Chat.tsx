import { useChat } from '@/contexts/chat';
import { usePrompt } from '@/contexts/prompt';
import analyticsService from '@/services/analytics';
import apiService from '@/services/api';
import { Message, MessageContent } from '@/types/chat';
import { isAbortError } from '@/utils/api';
import { useUser } from '@auth0/nextjs-auth0/client';
import {
  FC,
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from 'react';
import Button from '../Layout/Button';
import { Header } from '../Layout/Header';
import { ChatInput } from './ChatInput';
import { ChatKickoff } from './ChatKickoff';
import { ChatMessage } from './ChatMessage';
import { ChatNewMessage } from './ChatNewMessage';

export const Chat: FC = () => {
  const {
    messages,
    setMessages,
    loadingNewMessage,
    setFetchingNewMessage,
    loadingIframe,
    setLoadingIframe,
  } = useChat();
  const [newAssistantResponse, setNewAssistantResponse] =
    useState<Message | null>(null);
  const { user } = useUser();
  const { prompt, setPrompt } = usePrompt();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatAbortControllerRef = useRef<AbortController | null>();
  const [currentMessageContent, setCurrentMessageContent] =
    useState<MessageContent | null>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const sendMessage = useCallback(
    async (newUserMessage: string, isExample = false) => {
      const newMessage: Message = {
        role: 'user',
        content: newUserMessage,
      };
      const updatedMessages: Message[] = [...messages, newMessage];
      const abortController = new AbortController();
      chatAbortControllerRef.current = abortController;
      setFetchingNewMessage(true);
      setMessages(
        currentMessageContent
          ? [
              ...messages,
              {
                role: 'assistant',
                content: currentMessageContent,
              },
              newMessage,
            ]
          : updatedMessages,
      );
      setCurrentMessageContent({ status: 'loading' });

      try {
        const chatResponse = await apiService.chatStream(
          updatedMessages,
          user?.email || '',
          chatAbortControllerRef.current?.signal,
        );
        const reader = chatResponse.body?.getReader();
        let streamText = '';
        let isMessageFinished = false;

        if (typeof reader === 'undefined') {
          throw new Error('Variable "reader" is undefined.');
        }

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const text = new TextDecoder().decode(value);
          if (text.includes('###')) {
            isMessageFinished = true;
          }
          streamText += text;
          if (!isMessageFinished)
            setCurrentMessageContent({
              status: 'loading',
              generated_text: streamText,
            });
        }

        const rawResponse = streamText.split('###');
        // cached only return the later JSON
        const chatResponseJson =
          rawResponse.length == 2
            ? JSON.parse(rawResponse[1])
            : JSON.parse(rawResponse[0]);

        setCurrentMessageContent({
          status: chatResponseJson['status'],
          message: chatResponseJson['message'],
          generated_text: chatResponseJson['generated_text'],
          viz_id: chatResponseJson['viz_id'],
          id: chatResponseJson['log_id'],
        });
        analyticsService.buttonClick('new-user-prompt', {
          prompt: newUserMessage,
          status: chatResponseJson['status'],
          ['response-text']: chatResponseJson['generated_text'],
          ['response-viz-id']: chatResponseJson['viz_id'],
          ['response-id']: chatResponseJson['log_id'],
          ['is-example']: isExample,
        });
      } catch (e) {
        if (isAbortError(e)) {
          analyticsService.buttonClick('new-user-prompt', {
            prompt: newUserMessage,
            status: 'canceled',
            ['is-example']: isExample,
          });
          newCancelRequestMessage();
        } else {
          analyticsService.buttonClick('new-user-prompt', {
            prompt: newUserMessage,
            status: 'error',
            ['is-example']: isExample,
          });
          setNewAssistantResponse({
            role: 'assistant',
            content: {
              status: 'error',
              generated_text: 'Something went wrong. Please try again later.',
            },
          });
        }
        setCurrentMessageContent(null);
      } finally {
        setFetchingNewMessage(false);
      }
    },
    [messages, setMessages, setFetchingNewMessage, user],
  );

  const newCancelRequestMessage = () => {
    setNewAssistantResponse({
      role: 'assistant',
      content: {
        status: 'canceled',
        generated_text: 'User has cancelled the request.',
      },
    });
  };

  const handleExample = useCallback(
    (prompt: string) => {
      sendMessage(prompt, true);
    },
    [sendMessage],
  );

  const handleReset = useCallback(() => {
    setMessages([]);
    analyticsService.buttonClick('new-chat', {
      'messages-length': messages.length,
    });
  }, [messages, setMessages]);

  const handleAbort = () => {
    if (loadingIframe) {
      // data already fetched
      newCancelRequestMessage();
      setLoadingIframe(false);
    } else {
      if (chatAbortControllerRef.current) {
        chatAbortControllerRef.current.abort();
      }
    }
    setCurrentMessageContent(null);
  };

  useEffect(() => {
    if (newAssistantResponse) {
      setMessages((prevMessages) => {
        return [...prevMessages, newAssistantResponse];
      });
    }
    setNewAssistantResponse(null);
  }, [newAssistantResponse, setNewAssistantResponse, setMessages]);

  useEffect(() => {
    if (prompt) {
      handleExample(prompt);
      setPrompt(null);
    }
  }, [prompt, setPrompt, handleExample]);

  useLayoutEffect(() => {
    const timeout = setTimeout(() => scrollToBottom(), 100);
    return () => {
      clearTimeout(timeout);
    };
  }, [messages, loadingNewMessage, scrollToBottom]);

  return (
    <>
      {!messages.length ? (
        <div className="flex-1 flex flex-col gap-2 py-6 px-4 w-full max-w-[1000px] mx-auto">
          <Header title="Dataherald AI - Technical preview"></Header>
          <div className="flex-grow">
            <ChatKickoff onExampleClick={handleExample}></ChatKickoff>
          </div>
          <div className="sticky bottom-4 mt-4">
            <ChatInput onSend={sendMessage} />
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col">
          <div className="flex flex-col flex-grow">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
          </div>
          <div>
            {currentMessageContent && (
              <ChatNewMessage content={currentMessageContent} />
            )}
          </div>
          <div className="flex flex-col gap-4 items-center px-4 mb-4">
            {loadingNewMessage ? (
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
          </div>
          <div className="sticky bottom-4 w-full max-w-[1000px] px-4 mx-auto mb-4">
            <ChatInput onSend={sendMessage} />
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </>
  );
};
