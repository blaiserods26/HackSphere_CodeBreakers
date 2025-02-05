import { NextApiRequest, NextApiResponse } from 'next';
import { google } from 'googleapis';
import { serialize } from 'cookie';

const SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'];
const CLIENT_SECRETS_FILE = 'credentials.json';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { method } = req;

  if (method === 'GET') {
    try {
      const oAuth2Client = new google.auth.OAuth2(
        process.env.NEXT_PUBLIC_CLIENT_ID,
        process.env.NEXT_PUBLIC_CLIENT_SECRET,
        `${process.env.NEXT_PUBLIC_BASE_URL}/api/oauth/callback`
      );

      const authUrl = oAuth2Client.generateAuthUrl({
        access_type: 'offline',
        scope: SCOPES,
      });

      res.setHeader('Set-Cookie', serialize('oauth_state', oAuth2Client.credentials.state, { path: '/' }));
      res.redirect(authUrl);
    } catch (error) {
      res.status(500).json({ error: 'Error starting OAuth flow' });
    }
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${method} Not Allowed`);
  }
}
