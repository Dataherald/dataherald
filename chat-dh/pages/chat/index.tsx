import { Chat } from "@/components/Chat/Chat";
import { ChatKickoff } from "@/components/Chat/ChatKickoff";
import { Header } from "@/components/Layout/Header";
import { MainLayout } from "@/components/Layout/Main";
import { Message } from "@/types";
import Head from "next/head";
import { useEffect, useRef, useState } from "react";

export default function Home() {
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

    const response = await fetch("https://dev.api.dataherald.com/v5/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: updatedMessages,
      }),
    });

    if (!response.ok) {
      setLoading(false);
      throw new Error(response.statusText);
    }

    const data = await response.json();

    if (!data) {
      return;
    }

    setLoading(false);

    setMessages((messages) => [
      ...messages,
      {
        role: "assistant",
        content: data,
      },
    ]);

    // const reader = data.getReader();
    // const decoder = new TextDecoder();
    // let done = false;
    // let isFirst = true;

    // while (!done) {
    //   const { value, done: doneReading } = await reader.read();
    //   done = doneReading;
    //   const chunkValue = decoder.decode(value);

    //   if (isFirst) {
    //     isFirst = false;
    //     setMessages((messages) => [
    //       ...messages,
    //       {
    //         role: "assistant",
    //         content: chunkValue,
    //       },
    //     ]);
    //   } else {
    //     setMessages((messages) => {
    //       const lastMessage = messages[messages.length - 1];
    //       const updatedMessage = {
    //         ...lastMessage,
    //         content: lastMessage.content + chunkValue,
    //       };
    //       return [...messages.slice(0, -1), updatedMessage];
    //     });
    //   }
    // }
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
          content="A simple chatbot powered by OpenAPI that can generate text and visualizations with the latest data"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <MainLayout>
        <div className="flex-1 max-w-[900px] mx-auto px-2 mt-4 sm:mt-12 flex flex-col space-y-8">
          {!messages.length ? (
            <>
              <Header title="Dataherald AI for Real Estate"></Header>
              <div className="flex-grow">
                <ChatKickoff onExampleClick={handleExample}></ChatKickoff>
              </div>
              <Chat messages={messages} loading={loading} onSend={handleSend} />
            </>
          ) : (
            <div className="flex flex-grow">
              <Chat messages={messages} loading={loading} onSend={handleSend} />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </MainLayout>
    </>
  );
}
