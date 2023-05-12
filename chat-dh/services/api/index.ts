import { API_URL } from '@/env-variables';
import { ChatResponse } from '@/types/api';
import { Message } from '@/types/chat';
import { fetchAPI } from '@/utils/api';

const apiService = {
  async chat(
    message: Message[],
    userEmail: string = 'unknown',
    abortSignal: AbortSignal,
  ): Promise<ChatResponse> {
    // const url = "api/chat";
    const url = `${API_URL}/chat`;
    // HOTFIX -- Use directly our API because Vercel times out at 60s and can't be changed with our plan
    try {
      const response = await fetchAPI<ChatResponse>(url, {
        method: 'POST',
        body: {
          message,
          user: userEmail,
          date_entered: new Date(),
        },
        signal: abortSignal,
      });
      return response;
    } catch (error) {
      console.error(error);
      throw error;
    }
  },
  async feedback(chatResponseId: string, is_useful: boolean): Promise<void> {
    // const url = `api/chat/feedback/${chatResponseId}`;
    const url = `${API_URL}/chat/feedback/${chatResponseId}`;
    // HOTFIX -- Use directly our API because Vercel times out at 60s and can't be changed with our plan
    try {
      await fetchAPI<void>(url, {
        method: 'POST',
        body: {
          is_useful,
        },
      });
      return;
    } catch (error) {
      console.error(error);
      throw error;
    }
  },
  async login(user: {
    name: string;
    nickname: string;
    picture: string;
    email: string;
    email_verified: boolean;
  }): Promise<void> {
    const url = `${API_URL}/auth/login`;
    try {
      await fetchAPI<void>(url, {
        method: 'POST',
        body: {
          user,
        },
      });
      return;
    } catch (error) {
      console.error(error);
      throw error;
    }
  },
};

export default apiService;
