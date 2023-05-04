import { API_URL } from "@/env-variables";
import { ChatResponse } from "@/types/api";
import { Message } from "@/types/chat";
import { fetchAPI } from "@/utils/api";

const apiService = {
  async chat(
    message: Message[],
    userEmail: string = "unknown"
  ): Promise<ChatResponse> {
    const url = `${API_URL}/chat`;
    try {
      const response = await fetchAPI<ChatResponse>(url, {
        method: "POST",
        body: {
          message,
          user: userEmail,
          date_entered: new Date(),
        },
      });
      return response;
    } catch (error) {
      console.error(error);
      throw error;
    }
  },
  async feedback(chatResponseId: string, is_useful: boolean): Promise<void> {
    const url = `${API_URL}/chat/feedback/${chatResponseId}`;
    try {
      await fetchAPI<void>(url, {
        method: "POST",
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
};

export default apiService;
