import { NextApiRequest, NextApiResponse } from 'next';
import { google } from 'googleapis';
import { serialize } from 'cookie';
import { parse } from 'url';

const CLIENT_SECRETS_FILE = './credentials.json';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { method } = req;

  if (method === 'GET') {
    try {
      const oAuth2Client = new google.auth.OAuth2(
        process.env.NEXT_PUBLIC_CLIENT_ID,
        process.env.NEXT_PUBLIC_CLIENT_SECRET,
        `${process.env.NEXT_PUBLIC_BASE_URL}/api/oauth/callback`
      );

      const { query } = parse(req.url!, true);
      const { code } = query;

      if (!code) {
        res.status(400).json({ error: 'Missing code parameter' });
        return;
      }

      const { tokens } = await oAuth2Client.getToken(code as string);
      oAuth2Client.setCredentials(tokens);

      res.setHeader('Set-Cookie', serialize('oauth_token', tokens.access_token!, { path: '/' }));
      res.redirect('/analyze_emails');
    } catch (error) {
      res.status(500).json({ error: 'Error handling OAuth callback' });
    }
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${method} Not Allowed`);
  }
}
