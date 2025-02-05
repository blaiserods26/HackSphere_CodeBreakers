import { NextApiRequest, NextApiResponse } from "next";
import { OAuth2Client } from "google-auth-library";

const SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"];

const client = new OAuth2Client({
  clientId: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  redirectUri: process.env.GOOGLE_REDIRECT_URI,
});

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === "GET") {
    const authUrl = client.generateAuthUrl({
      access_type: "offline",
      scope: SCOPES,
    });
    res.redirect(authUrl);
  } else {
    res.status(405).end(); // Method Not Allowed
  }
}
