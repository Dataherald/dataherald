import { API_URL } from "@/env-variables";
import { getSession } from "@auth0/nextjs-auth0";
import { NextApiRequest, NextApiResponse } from "next";

/**
 * UNUSED FOR NOW
 */
async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const session = getSession(req, res);

    if (!session) {
      res.status(401).json({ message: "Unauthorized" });
      return;
    }

    if (req.method === "POST") {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: req.body.updatedMessages,
        }),
      });

      if (!response.ok) {
        res.status(response.status).json({ message: response.statusText });
        return;
      }

      const data = await response.json();
      res.status(200).json(data);
    } else {
      res.status(405).json({ message: "Method Not Allowed" });
    }
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: "Internal Server Error" });
  }
}

export default handler;
