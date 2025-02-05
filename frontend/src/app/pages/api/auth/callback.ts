import { NextApiRequest, NextApiResponse } from 'next';
import { google } from 'google-auth-library';
import { OAuth2Client } from 'google-auth-library';
import { setCookie } from 'nookies';

const SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'];
const CLIENT_SECRETS_FILE = './credentials.json';

const client = new OAuth2Client({
  keyFile: CLIENT_SECRETS_FILE,
  scopes: SCOPES,
});

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { code } = req.query;

  if (!code) {
    res.status(400).send('Missing code parameter');
    return;
  }

  try {
    const { tokens } = await client.getToken(code as string);
    client.setCredentials(tokens);

    // Save credentials in cookies
    setCookie({ res }, 'token', JSON.stringify(tokens), {
      httpOnly: true,
      secure: process.env.NODE_ENV !== 'development',
      maxAge: 60 * 60 * 24 * 30, // 30 days
      path: '/',
    });

    res.redirect('/analyze-emails');
  } catch (error) {
    res.status(500).send(`Error in OAuth callback: ${error.message}`);
  }
}