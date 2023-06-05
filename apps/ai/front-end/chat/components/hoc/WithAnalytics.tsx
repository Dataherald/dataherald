import analyticsService from '@/services/analytics';
import { useUser } from '@auth0/nextjs-auth0/client';
import { useRouter } from 'next/router';
import { FC, ReactNode, useEffect } from 'react';

type WithAnalyticsProps = {
  children: ReactNode;
};

const WithAnalytics: FC<WithAnalyticsProps> = ({ children }) => {
  const router = useRouter();
  const { user, error } = useUser();

  useEffect(() => {
    if (error) {
      console.error('Error fetching user:', error);
      return;
    }
    if (user) {
      analyticsService.setUser(user);
    }
  }, [user, error, router]);

  return <>{children}</>;
};

export default WithAnalytics;
