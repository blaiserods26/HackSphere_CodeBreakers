import NextAuth from 'next-auth';
import { JWT } from 'next-auth/jwt';
import { Session } from 'next-auth';
import { Account } from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';

interface Token extends JWT {
  accessToken?: string;
  refreshToken?: string;
  accessTokenExpires?: number;
  error?: string;
}

export default NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: 'openid email profile https://www.googleapis.com/auth/gmail.readonly',
          access_type: 'offline',
          prompt: 'consent',
        },
      },
    }),
  ],
  callbacks: {
    async jwt({ token, account }: { token: Token; account?: Account }) {
      if (account) {
        token.accessToken = account.access_token!;
        token.refreshToken = account.refresh_token!;
        token.accessTokenExpires = account.expires_at ? account.expires_at * 1000 : undefined;
      }

      if (token.accessTokenExpires && Date.now() < token.accessTokenExpires) {
        return token;
      } else {
        return await refreshAccessToken(token);
      }
    },

    async session({ session, token }: { session: Session; token: Token }) {
      session.accessToken = token.accessToken;
      session.refreshToken = token.refreshToken;
      session.error = token.error;

      return session;
    },
  },
});

async function refreshAccessToken(token: Token): Promise<Token> {
  try {
    const url = 'https://oauth2.googleapis.com/token?' + new URLSearchParams({
      client_id: process.env.GOOGLE_CLIENT_ID!,
      client_secret: process.env.GOOGLE_CLIENT_SECRET!,
      grant_type: 'refresh_token',
      refresh_token: token.refreshToken!,
    });

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      method: 'POST',
    });

    const refreshedTokens = await response.json();

    if (!response.ok) {
      throw refreshedTokens;
    }

    return {
      ...token,
      accessToken: refreshedTokens.access_token,
      accessTokenExpires: Date.now() + refreshedTokens.expires_in * 1000,
      refreshToken: refreshedTokens.refresh_token ?? token.refreshToken,
    };
  } catch (error) {
    console.error('Error refreshing access token:', error);

    return {
      ...token,
      error: 'RefreshAccessTokenError',
    };
  }
}