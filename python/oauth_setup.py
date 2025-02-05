from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os
import json
from flask import Flask, request, redirect, session, url_for

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
            access_type='offline',
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
        
        # Save credentials
        save_credentials(credentials)
        
        return redirect(url_for('analyze_emails'))
    
    except Exception as e:
        return f"Error in OAuth callback: {str(e)}"

def save_credentials(credentials):
    """Save credentials to a file."""
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

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for development
    app.run(debug=True, port=5000) 