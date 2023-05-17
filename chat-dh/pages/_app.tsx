import { PromptProvider } from '@/context/prompt';
import analyticsService from '@/services/analytics';
import '@/styles/globals.css';
import { UserProvider } from '@auth0/nextjs-auth0/client';
import type { AppProps } from 'next/app';
import { Lato } from 'next/font/google';
import { useEffect } from 'react';

const lato = Lato({
  weight: ['100', '300', '400', '700', '900'],
  style: ['normal', 'italic'],
  subsets: ['latin'],
});

export default function App({ Component, pageProps }: AppProps) {
  const { user } = pageProps;

  useEffect(() => {
    if (user) {
      analyticsService.setUser(user);
    }
  }, [user]);

  return (
    <UserProvider user={user}>
      <PromptProvider>
        <main className={lato.className}>
          <Component {...pageProps} />
        </main>
      </PromptProvider>
    </UserProvider>
  );
}
