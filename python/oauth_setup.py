from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os
import json
from flask import Flask, request, redirect, session, url_for
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
    """Home page with login button."""
    return '''
        <h1>Email Security Analysis Tool</h1>
        <a href="/authorize"><button>Login with Gmail</button></a>
    '''

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
            # Request offline access to get refresh token
            access_type='offline',
            # Force to always get refresh_token
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
        
        # Use the authorization server's response to fetch the OAuth 2.0 tokens
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
        
        credentials = flow.credentials
        
        # Save credentials with all necessary fields
        creds_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Save to token.json
        with open('token.json', 'w') as token_file:
            json.dump(creds_data, token_file)
        
        # Redirect to emails page instead of analyze_emails
        return redirect(url_for('display_emails'))
    
    except Exception as e:
        return f"Error in OAuth callback: {str(e)}"

@app.route('/analyze_emails')
def analyze_emails():
    """Analyze emails using saved credentials."""
    try:
        # Load saved credentials
        with open('token.json', 'r') as token_file:
            creds_data = json.load(token_file)
        
        # Import the email analysis function
        from email_security_tool import analyze_emails
        
        # Run the analysis
        results = analyze_emails(creds_data)
        
        # Convert results to formatted HTML
        html_results = format_results_as_html(results)
        
        return f'''
            <h1>Email Analysis Results</h1>
            {html_results}
            <br>
            <a href="/"><button>Back to Home</button></a>
        '''
    
    except Exception as e:
        return f"Error analyzing emails: {str(e)}"

def format_results_as_html(results):
    """Format the JSON results as HTML."""
    if 'error' in results:
        return f"<p>Error: {results['error']}</p>"
    
    html = f"<p>Total Emails Analyzed: {results['total_emails_analyzed']}</p>"
    
    for i, result in enumerate(results['results'], 1):
        html += f'''
            <div style="border: 1px solid #ccc; margin: 10px; padding: 10px;">
                <h3>Email {i}</h3>
                <p>From: {result['email_info']['sender']}</p>
                <p>Subject: {result['email_info']['subject']}</p>
                <p>Overall Risk Score: {result['overall_risk_score']}</p>
                
                <h4>Security Analysis</h4>
                <p>Score: {result['security_analysis']['overall_score']}</p>
                <p>Grade: {result['security_analysis']['overall_grade']}</p>
                
                <h4>Link Analysis</h4>
                <p>Total Links: {result['link_analysis']['total_links']}</p>
                <p>Suspicious Links: {len(result['link_analysis']['suspicious_links'])}</p>
                
                <h4>Attachment Analysis</h4>
                {format_attachments(result['attachment_analysis'])}
            </div>
        '''
    
    return html

def format_attachments(attachments):
    """Format attachment results as HTML."""
    if not attachments:
        return "<p>No attachments found</p>"
    
    html = "<ul>"
    for filename, info in attachments.items():
        html += f'''
            <li>
                {filename}: 
                <span style="color: {'green' if info['status'] == 'Safe' else 'red'}">
                    {info['status']}
                </span>
                - {info['details']}
            </li>
        '''
    html += "</ul>"
    return html

def get_email_list(credentials):
    """Fetch emails using Gmail API."""
    try:
        # Build the Gmail service
        service = build('gmail', 'v1', credentials=credentials)
        
        # Request emails from user's inbox
        results = service.users().messages().list(userId='me', maxResults=20).execute()
        messages = results.get('messages', [])

        email_list = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            
            # Extract email headers
            headers = msg['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
            sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown Sender')
            date = datetime.fromtimestamp(int(msg['internalDate'])/1000).strftime('%Y-%m-%d %H:%M:%S')

            # Extract full email body (both plain text and HTML)
            plain_body = ''
            html_body = ''
            
            def get_body_from_part(part):
                if 'data' in part.get('body', {}):
                    return base64.urlsafe_b64decode(part['body']['data']).decode()
                return ''

            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        plain_body = get_body_from_part(part)
                    elif part['mimeType'] == 'text/html':
                        html_body = get_body_from_part(part)
            elif 'body' in msg['payload']:
                if msg['payload']['mimeType'] == 'text/plain':
                    plain_body = get_body_from_part(msg['payload'])
                elif msg['payload']['mimeType'] == 'text/html':
                    html_body = get_body_from_part(msg['payload'])

            email_list.append({
                'id': message['id'],
                'subject': subject,
                'sender': sender,
                'date': date,
                'preview': plain_body[:200] + '...' if len(plain_body) > 200 else plain_body,
                'plain_body': plain_body,
                'html_body': html_body,
                'labels': msg['labelIds']
            })

        return email_list

    except Exception as e:
        return {'error': str(e)}

@app.route('/emails')
def display_emails():
    """Display emails in a formatted table."""
    try:
        # Load saved credentials
        with open('token.json', 'r') as token_file:
            creds_data = json.load(token_file)
        
        # Create proper Credentials object
        credentials = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data['refresh_token'],
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=creds_data['scopes']
        )
        
        # If credentials are expired, refresh them
        if credentials.expired:
            credentials.refresh(Request())
            # Save refreshed credentials
            with open('token.json', 'w') as token_file:
                json.dump(creds_data, token_file)
        
        # Get emails
        emails = get_email_list(credentials)
        
        if isinstance(emails, dict) and 'error' in emails:
            return f"Error fetching emails: {emails['error']}"

        # Create HTML
        html = '''
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .email-list { max-width: 1000px; margin: 0 auto; }
            .email-item {
                border: 1px solid #ddd;
                margin-bottom: 10px;
                padding: 10px;
                cursor: pointer;
            }
            .email-header {
                display: flex;
                justify-content: space-between;
                padding: 5px;
            }
            .email-content {
                display: none;
                padding: 10px;
                background-color: #f9f9f9;
                margin-top: 10px;
            }
            .analyze-btn {
                background-color: #4CAF50;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
                cursor: pointer;
            }
            .analyze-btn:hover {
                background-color: #45a049;
            }
            .email-meta {
                color: #666;
                font-size: 0.9em;
            }
        </style>

        <div class="email-list">
            <h1>Your Emails</h1>
        '''
        
        for email in emails:
            html += f'''
            <div class="email-item">
                <div class="email-header" onclick="toggleEmail('{email['id']}')">
                    <div>
                        <strong>{email['subject']}</strong>
                        <div class="email-meta">
                            From: {email['sender']}
                            <br>
                            Date: {email['date']}
                        </div>
                    </div>
                    <button class="analyze-btn" onclick="analyzeEmail(event, '{email['id']}')">
                        Analyze
                    </button>
                </div>
                <div id="content-{email['id']}" class="email-content">
                    {email['html_body'] if email['html_body'] else email['plain_body']}
                </div>
            </div>
            '''

        html += '''
        </div>

        <script>
            function toggleEmail(id) {
                const content = document.getElementById('content-' + id);
                const currentDisplay = content.style.display;
                
                // Close all email contents
                document.querySelectorAll('.email-content').forEach(el => {
                    el.style.display = 'none';
                });
                
                // Open clicked email if it wasn't already open
                if (currentDisplay !== 'block') {
                    content.style.display = 'block';
                }
            }
            
            function analyzeEmail(event, id) {
                event.stopPropagation();
                window.location.href = `/analyze_single_email/${id}`;
            }
        </script>
        '''
        
        return html

    except Exception as e:
        return f"Error displaying emails: {str(e)}"

@app.route('/analyze_single_email/<email_id>')
def analyze_single_email(email_id):
    """Analyze a single email."""
    try:
        # Load credentials
        with open('token.json', 'r') as token_file:
            creds_data = json.load(token_file)
        
        # Create Gmail service
        credentials = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data['refresh_token'],
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=creds_data['scopes']
        )
        
        service = build('gmail', 'v1', credentials=credentials)
        
        # Get the specific email
        message = service.users().messages().get(userId='me', id=email_id, format='full').execute()
        
        # Extract email details
        headers = message['payload']['headers']
        sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown')
        subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
        
        # Extract sender email from the "From" field
        sender_email = re.search(r'<(.+?)>', sender)
        if sender_email:
            sender_email = sender_email.group(1)
        else:
            sender_email = sender
        
        # Import and use the email analysis function
        from email_security_tool import EmailSecurityAnalyzer
        
        analyzer = EmailSecurityAnalyzer()
        security_results = analyzer.comprehensive_email_security_analysis(sender_email)
        
        # Analyze attachments if present
        attachment_results = {}
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if 'filename' in part and part['filename']:
                    filename = part['filename']
                    if 'body' in part and 'attachmentId' in part['body']:
                        attachment = service.users().messages().attachments().get(
                            userId='me',
                            messageId=email_id,
                            id=part['body']['attachmentId']
                        ).execute()
                        
                        # Save attachment temporarily
                        file_data = base64.urlsafe_b64decode(attachment['data'])
                        temp_path = os.path.join("attachments", f"temp_{filename}")
                        
                        with open(temp_path, 'wb') as f:
                            f.write(file_data)
                        
                        # Scan with VirusTotal
                        from email_security_tool import scan_file_virustotal
                        is_safe, scan_details = scan_file_virustotal(temp_path)
                        
                        attachment_results[filename] = {
                            "status": "Safe" if is_safe else "Suspicious",
                            "details": scan_details
                        }
                        
                        # Clean up
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
        
        # Analyze links in email body
        body = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] in ['text/plain', 'text/html']:
                    if 'data' in part['body']:
                        body += base64.urlsafe_b64decode(part['body']['data']).decode()
        elif 'body' in message['payload']:
            if 'data' in message['payload']['body']:
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode()
        
        from email_security_tool import analyze_links
        link_analysis = analyze_links(body)
        
        # Prepare complete analysis results
        analysis_results = {
            'total_emails_analyzed': 1,
            'results': [{
                'email_info': {
                    'sender': sender,
                    'subject': subject
                },
                'security_analysis': security_results,
                'link_analysis': link_analysis,
                'attachment_analysis': attachment_results,
                'overall_risk_score': calculate_risk_score(
                    security_results['overall_score'],
                    link_analysis['risk_score'],
                    len([a for a in attachment_results.values() if a['status'] == 'Suspicious'])
                )
            }]
        }
        
        # Convert results to formatted HTML
        html_results = format_results_as_html(analysis_results)
        
        return f'''
            <h1>Email Analysis Results</h1>
            {html_results}
            <br>
            <a href="/emails"><button>Back to Emails</button></a>
        '''
    
    except Exception as e:
        return f"Error analyzing email: {str(e)}"

def calculate_risk_score(security_score, link_risk_score, suspicious_attachments):
    """Calculate overall risk score."""
    security_risk = 100 - security_score
    weighted_security = security_risk * 0.4
    weighted_links = link_risk_score * 0.3
    weighted_attachments = (suspicious_attachments * 25) * 0.3
    
    total_risk = weighted_security + weighted_links + weighted_attachments
    return min(100, total_risk)  # Cap at 100

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for development
    app.run(debug=True, port=5000) 