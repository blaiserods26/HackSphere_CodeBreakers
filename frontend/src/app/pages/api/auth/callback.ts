import { NextApiRequest, NextApiResponse } from 'next';
import { OAuth2Client } from 'google-auth-library';
import { setCookie } from 'nookies';

const SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'];

const client = new OAuth2Client({
  clientId: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  redirectUri: process.env.GOOGLE_REDIRECT_URI,
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
    const errorMessage = (error as Error).message;
    res.status(500).send(`Error in OAuth callback: ${errorMessage}`);
  }
}