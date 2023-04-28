import { Chat } from "@/components/Chat/Chat";
import { ChatKickoff } from "@/components/Chat/ChatKickoff";
import { Header } from "@/components/Layout/Header";
import { MainLayout } from "@/components/Layout/Main";
import apiService from "@/services/api";
import { Message } from "@/types/chat";
import { withPageAuthRequired } from "@auth0/nextjs-auth0/client";
import Head from "next/head";
import { useEffect, useRef, useState } from "react";

export default withPageAuthRequired(function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSend = async (message: Message) => {
    const updatedMessages = [...messages, message];

    setMessages(updatedMessages);
    setLoading(true);

    const chatResponse = await apiService.chat(updatedMessages);

    if (!chatResponse) {
      return;
    }

    setLoading(false);

    setMessages((messages) => [
      ...messages,
      {
        role: "assistant",
        content: chatResponse,
      },
    ]);
  };

  const handleExample = (prompt: string) => {
    handleSend({
      role: "user",
      content: prompt,
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <>
      <Head>
        <title>ChatDH - Dataherald</title>
        <meta
          name="description"
          content="A chatbot powered by OpenAPI that can generate text and visualizations with the latest data"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <MainLayout>
        {!messages.length ? (
          <div className="flex-1 flex flex-col gap-6 py-6 sm:pt-12">
            <Header title="Dataherald AI for Real Estate"></Header>
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
