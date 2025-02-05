import { NextApiRequest, NextApiResponse } from 'next';
import { google } from 'google-auth-library';
import { OAuth2Client } from 'google-auth-library';

const SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'];
const CLIENT_SECRETS_FILE = './credentials.json';

const client = new OAuth2Client({
  keyFile: CLIENT_SECRETS_FILE,
  scopes: SCOPES,
});

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    const authUrl = client.generateAuthUrl({
      access_type: 'offline',
      scope: SCOPES,
    });
    res.redirect(authUrl);
  } else {
    res.status(405).end(); // Method Not Allowed
  }
}