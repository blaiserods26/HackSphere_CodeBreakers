import { google, gmail_v1 } from 'googleapis';

export async function analyzeEmails(auth: any) {
  const gmail = google.gmail({ version: 'v1', auth });
  const res = await gmail.users.messages.list({ userId: 'me', maxResults: 10 });
  const messages = res.data.messages || [];

  const results = await Promise.all(
    messages.map(async (message) => {
      const response = await gmail.users.messages.get({ userId: 'me', id: message.id });
      const emailData = response.data as gmail_v1.Schema$Message;
      // Perform your email analysis here
      return {
        id: emailData.id,
        snippet: emailData.snippet,
        // Add more analysis results as needed
      };
    })
  );

  return {
    total_emails_analyzed: messages.length,
    results,
  };
}