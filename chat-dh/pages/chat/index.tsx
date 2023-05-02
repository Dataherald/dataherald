import { Chat } from "@/components/Chat/Chat";
import { ChatKickoff } from "@/components/Chat/ChatKickoff";
import { Header } from "@/components/Layout/Header";
import { MainLayout } from "@/components/Layout/Main";
import { usePrompt } from "@/context/prompt";
import apiService from "@/services/api";
import { Message, MessageContent } from "@/types/chat";
import { useUser, withPageAuthRequired } from "@auth0/nextjs-auth0/client";
import Head from "next/head";
import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from "react";

export default withPageAuthRequired(function Home() {
  const { prompt, setPrompt } = usePrompt();
  const { user } = useUser();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSend = useCallback(
    async (message: Message) => {
      const updatedMessages: Message[] = [...messages, message];
      setLoading(true);
      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content: {
            status: "loading",
          },
        },
      ]);
      try {
        const chatResponse = await apiService.chat(
          updatedMessages,
          user?.email || ""
        );
        setMessages((messages) =>
          messages.map((message) =>
            (message.content as MessageContent).status === "loading"
              ? {
                  role: "assistant",
                  content: chatResponse,
                }
              : message
          )
        );
      } catch (e) {
        setMessages((messages) =>
          messages.map((message) =>
            (message.content as MessageContent).status === "loading"
              ? {
                  role: "assistant",
                  content: {
                    status: "error",
                    generated_text:
                      "Something went wrong. Please try again later.",
                  },
                }
              : message
          )
        );
      } finally {
        setLoading(false);
      }
    },
    [messages, user]
  );

  const handleExample = useCallback(
    (prompt: string) => {
      handleSend({
        role: "user",
        content: prompt,
      });
    },
    [handleSend]
  );

  useLayoutEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    if (prompt) {
      handleExample(prompt);
      setPrompt(null);
    }
  }, [prompt, handleExample, setPrompt]);

  return (
    <>
      <Head>
        <title>Dataherald AI | Chat</title>
        <meta
          name="description"
          content="A chatbot powered by OpenAPI that can generate text and visualizations with the latest data"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <MainLayout>
        {!messages.length ? (
          <div className="flex-1 flex flex-col gap-2 py-6">
            <Header title="Dataherald AI - Technical preview"></Header>
            <div className="flex-grow">
              <ChatKickoff onExampleClick={handleExample}></ChatKickoff>
            </div>
            <Chat messages={messages} loading={loading} onSend={handleSend} />
          </div>
        ) : (
          <div className="flex-1 flex flex-col mb-4">
            <Chat messages={messages} loading={loading} onSend={handleSend} />
          </div>
        )}
        <div ref={messagesEndRef} />
      </MainLayout>
    </>
  );
});
