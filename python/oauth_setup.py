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
    """Display emails in a formatted table with security status."""
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
            with open('token.json', 'w') as token_file:
                json.dump(creds_data, token_file)
        
        # Get emails
        emails = get_email_list(credentials)
        
        if isinstance(emails, dict) and 'error' in emails:
            return f"Error fetching emails: {emails['error']}"

        html = '''
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0;
                padding: 20px;
                background-color: #fff;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                padding: 10px 0;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 30px;
                border-bottom: 1px solid #e0e0e0;
            }
            .nav-links {
                display: flex;
                gap: 30px;
                align-items: center;
                padding: 0 20px;
            }
            .nav-link {
                text-decoration: none;
                color: #202124;
                font-size: 14px;
                display: flex;
                align-items: center;
            }
            .nav-link.all {
                color: #1a73e8;
            }
            .nav-link.safe {
                color: #137333;
            }
            .nav-link.unsafe {
                color: #c5221f;
            }
            .nav-link svg {
                margin-right: 4px;
            }
            .email-list {
                list-style: none;
                margin: 0;
                padding: 0;
            }
            .email-item {
                display: flex;
                align-items: center;
                padding: 8px 16px;
                border-bottom: 1px solid #f1f3f4;
                min-height: 40px;
            }
            .email-item:hover {
                box-shadow: inset 1px 0 0 #dadce0, inset -1px 0 0 #dadce0, 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
                z-index: 1;
                position: relative;
            }
            .email-checkbox {
                margin-right: 16px;
            }
            .email-star {
                color: #5f6368;
                margin-right: 16px;
                font-size: 18px;
            }
            .email-content {
                flex-grow: 1;
                display: flex;
                align-items: center;
                min-width: 0;
                gap: 100px;
            }
            .email-sender {
                width: 200px;
                font-size: 14px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .email-middle {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                min-width: 0;
            }
            .email-subject {
                color: #202124;
                font-size: 14px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .email-preview {
                color: #5f6368;
                font-size: 14px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .email-meta {
                display: flex;
                align-items: center;
                gap: 12px;
                min-width: 120px;
                justify-content: flex-end;
            }
            .email-time {
                color: #5f6368;
                font-size: 12px;
                white-space: nowrap;
            }
            .status-badge {
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: 500;
                text-transform: uppercase;
            }
            .status-safe {
                background-color: #e6f4ea;
                color: #137333;
            }
            .status-unsafe {
                background-color: #fce8e6;
                color: #c5221f;
            }
            .email-count {
                color: #5f6368;
                font-size: 13px;
                margin-left: auto;
            }
        </style>

        <div class="container">
            <div class="header">
                <nav class="nav-links">
                    <a href="/emails" class="nav-link all">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                        </svg>
                        All
                    </a>
                    <a href="/emails?filter=safe" class="nav-link safe">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                        </svg>
                        Safe
                    </a>
                    <a href="/emails?filter=unsafe" class="nav-link unsafe">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="12" y1="8" x2="12" y2="12"></line>
                            <line x1="12" y1="16" x2="12.01" y2="16"></line>
                        </svg>
                        Unsafe
                    </a>
                </nav>
                <span class="email-count">1-5 of 5</span>
            </div>

            <ul class="email-list">
        '''
        
        for email in emails:
            # Determine email security status based on certain keywords or patterns
            is_safe = not any(keyword in email['subject'].lower() for keyword in ['chai', 'coding ninjas'])
            status_class = "status-safe" if is_safe else "status-unsafe"
            status_text = "SAFE" if is_safe else "UNSAFE"
            
            html += f'''
                <li class="email-item">
                    <input type="checkbox" class="email-checkbox">
                    <span class="email-star">☆</span>
                    <div class="email-content">
                        <div class="email-sender">{email['sender']}</div>
                        <div class="email-middle">
                            <div class="email-subject">{email['subject']}</div>
                            <div class="email-preview">{email['preview']}</div>
                        </div>
                        <div class="email-meta">
                            <span class="email-time">{email['date'].split()[1]}</span>
                            <span class="status-badge {status_class}">{status_text}</span>
                        </div>
                    </div>
                </li>
            '''

        html += '''
            </ul>
        </div>
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