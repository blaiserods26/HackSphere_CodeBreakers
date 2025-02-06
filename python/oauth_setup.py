from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os
import json
from flask import Flask, request, redirect, session, url_for, send_file
from googleapiclient.discovery import build
from datetime import datetime
import base64
from google.auth.transport.requests import Request
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# OAuth 2.0 configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CLIENT_SECRETS_FILE = "./credentials.json"

@app.route('/')
def index():
    """Home page with login form."""
    return send_file('index.html')

@app.route('/authorize')
def authorize():
    """Start the OAuth flow."""
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=url_for('oauth2callback', _external=True)
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            include_granted_scopes='true'
        )
        
        session['state'] = state
        return redirect(authorization_url)
    
    except Exception as e:
        return f"Error starting OAuth flow: {str(e)}"

@app.route('/oauth2callback')
def oauth2callback():
    """Handle the OAuth 2.0 callback."""
    try:
        state = session['state']
        
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=state,
            redirect_uri=url_for('oauth2callback', _external=True)
        )
        
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
        
        credentials = flow.credentials
        
        creds_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        with open('token.json', 'w') as token_file:
            json.dump(creds_data, token_file)
        
        return redirect(url_for('display_emails'))
    
    except Exception as e:
        return f"Error in OAuth callback: {str(e)}"

def get_email_list(credentials):
    """Fetch emails using Gmail API."""
    try:
        service = build('gmail', 'v1', credentials=credentials)
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])

        email_list = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            headers = msg['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
            sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown Sender')
            date = datetime.fromtimestamp(int(msg['internalDate'])/1000).strftime('%Y-%m-%d %H:%M:%S')

            email_list.append({
                'id': message['id'],
                'subject': subject,
                'sender': sender,
                'date': date
            })

        return email_list

    except Exception as e:
        return {'error': str(e)}

@app.route('/emails')
def display_emails():
    """Display emails using the design from email-inbox.html."""
    try:
        with open('token.json', 'r') as token_file:
            creds_data = json.load(token_file)
        
        credentials = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data['refresh_token'],
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=creds_data['scopes']
        )
        
        if credentials.expired:
            credentials.refresh(Request())
            with open('token.json', 'w') as token_file:
                json.dump(creds_data, token_file)
        
        emails = get_email_list(credentials)
        
        if isinstance(emails, dict) and 'error' in emails:
            return f"Error fetching emails: {emails['error']}"

        # Use the HTML structure from email-inbox.html
        html = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Security Inbox</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: system-ui, -apple-system, sans-serif;
                }

                body {
                    min-height: 100vh;
                    background: linear-gradient(to bottom right, #EBF4FF, #E6F0FF);
                }

                .container {
                    max-width: 1200px;
                    margin: 2rem auto;
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                    display: flex;
                }

                .sidebar {
                    width: 250px;
                    background: white;
                    border-right: 1px solid #e5e7eb;
                    padding: 1.5rem;
                }

                .compose-btn {
                    width: 100%;
                    padding: 0.75rem;
                    background: #0074c6;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 500;
                    cursor: pointer;
                    margin-bottom: 1.5rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 0.5rem;
                    transition: background 0.2s;
                }

                .compose-btn:hover {
                    background: #0066b2;
                }

                .nav-item {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    padding: 0.75rem;
                    border-radius: 8px;
                    cursor: pointer;
                    color: #666;
                    margin-bottom: 0.5rem;
                    transition: all 0.2s;
                }

                .nav-item:hover {
                    background: #f0f9ff;
                    color: #0074c6;
                }

                .nav-item.active {
                    background: #f0f9ff;
                    color: #0074c6;
                }

                .main-content {
                    flex: 1;
                    background: white;
                }

                .email-list {
                    list-style: none;
                }

                .email-header {
                    padding: 1rem;
                    border-bottom: 1px solid #e5e7eb;
                    color: #666;
                    font-size: 0.875rem;
                }

                .email-item {
                    display: flex;
                    align-items: center;
                    padding: 1rem;
                    border-bottom: 1px solid #e5e7eb;
                    cursor: pointer;
                    transition: all 0.2s;
                }

                .email-item:hover {
                    background: #f8fafc;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }

                .checkbox {
                    margin-right: 1rem;
                }

                .star-btn {
                    background: none;
                    border: none;
                    cursor: pointer;
                    color: #d1d5db;
                    margin-right: 1rem;
                    padding: 0.25rem;
                }

                .star-btn.starred {
                    color: #fbbf24;
                }

                .email-content {
                    flex: 1;
                    min-width: 0;
                }

                .email-top {
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    margin-bottom: 0.25rem;
                }

                .sender {
                    font-weight: 500;
                    width: 200px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }

                .subject {
                    flex: 1;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }

                .time {
                    color: #666;
                    font-size: 0.875rem;
                    margin-right: 1rem;
                }

                .safety-badge {
                    padding: 0.25rem 0.75rem;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    font-weight: 500;
                }

                .safety-badge.safe {
                    background: #ecfdf5;
                    color: #059669;
                }

                .safety-badge.unsafe {
                    background: #fef2f2;
                    color: #dc2626;
                }

                .preview {
                    color: #666;
                    font-size: 0.875rem;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="sidebar">
                    <button class="compose-btn">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 5v14M5 12h14"/>
                        </svg>
                        Compose
                    </button>

                    <div class="nav-item active" data-filter="all">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                        </svg>
                        All
                    </div>

                    <div class="nav-item" data-filter="safe">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        </svg>
                        Safe
                    </div>

                    <div class="nav-item" data-filter="unsafe">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/>
                            <line x1="12" y1="8" x2="12" y2="12"/>
                            <line x1="12" y1="16" x2="12.01" y2="16"/>
                        </svg>
                        Unsafe
                    </div>
                </div>

                <div class="main-content">
                    <div class="email-header">
                        1-{len(emails)} of {len(emails)}
                    </div>
                    <div class="email-list">
        '''

        for email in emails:
            html += f'''
                        <div class="email-item" data-id="{email['id']}">
                            <input type="checkbox" class="checkbox">
                            <button class="star-btn">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                                </svg>
                            </button>
                            <div class="email-content">
                                <div class="email-top">
                                    <span class="sender">{email['sender']}</span>
                                    <span class="subject">{email['subject']}</span>
                                    <span class="time">{email['date']}</span>
                                    <span class="safety-badge safe">SAFE</span>
                                </div>
                                <div class="preview">This is a preview of the email content...</div>
                            </div>
                        </div>
            '''

        html += '''
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''

        return html

    except Exception as e:
        return f"Error displaying emails: {str(e)}"

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for development
    app.run(debug=True, port=5000) 