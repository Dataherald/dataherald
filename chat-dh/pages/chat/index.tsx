import { Chat } from '@/components/Chat/Chat';
import { MainLayout } from '@/components/Layout/Main';
import { ChatProvider } from '@/context/chat';
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client';
import Head from 'next/head';

export default withPageAuthRequired(function Home() {
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

      <MainLayout mode="full">
        <ChatProvider>
          <Chat />
        </ChatProvider>
      </MainLayout>
    </>
  );
});
