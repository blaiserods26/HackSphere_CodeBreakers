// pages/api/gmail.js

import { getToken } from "next-auth/jwt";
import { google } from "googleapis";
import { signIn } from "next-auth/react";
import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const token = await getToken({ req });
  
  if (!token) {
    res.status(401).json({ error: "Unauthorized" });
    return;
  }
 if (token.error === "RefreshAccessTokenError") {
   res.status(401).json({ error: "Token expired. Please sign in again." });
   return;
 }
  try {
    const oauth2Client = new google.auth.OAuth2();
    oauth2Client.setCredentials({
      access_token: token.accessToken as string,
    });

    const gmail = google.gmail({ version: "v1", auth: oauth2Client });

    // Fetch the list of messages
    const response = await gmail.users.messages.list({
      userId: "me",
      maxResults: 10,
    });

    const messages = response.data.messages || [];

    // Fetch details for each message
    const emails = await Promise.all(
      messages.map(async (message) => {
        const msg = await gmail.users.messages.get({
            userId: "me",
            id: message.id as string,
            format: "metadata",
            metadataHeaders: ["Subject", "From", "To", "Date"],
        });
        return msg.data;
      })
    );

    res.status(200).json({ emails });
  } catch (error) {
    console.error("Error fetching emails:", error);
    res.status(500).json({ error: "Error fetching emails" });
  }
}
