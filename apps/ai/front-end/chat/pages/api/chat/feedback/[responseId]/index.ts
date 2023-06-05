import { API_URL } from '@/env-variables';
import { ChatResponse } from '@/types/api';
import { fetchAPI } from '@/utils/api';
import { withApiAuthRequired } from '@auth0/nextjs-auth0';
import { NextApiRequest, NextApiResponse } from 'next';

export default withApiAuthRequired(
  async (req: NextApiRequest, res: NextApiResponse) => {
    const { responseId } = req.query;
    const url = `${API_URL}/chat/feedback/${responseId}`;
    if (req.method === 'POST') {
      try {
        const { is_useful } = req.body;
        const chatResponse = await fetchAPI<ChatResponse>(url, {
          method: 'POST',
          body: {
            is_useful,
          },
        });
        res.status(201).json(chatResponse);
      } catch (error) {
        res.status(500).json({ error: error });
      }
    } else {
      res.setHeader('Allow', ['POST']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
    }
  },
);
