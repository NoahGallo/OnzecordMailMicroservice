from flask import Flask, request, jsonify, render_template
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from flask_swagger_ui import get_swaggerui_blueprint

# Initialize Flask app
app = Flask(__name__)

#Swagger

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
)

app.register_blueprint(swaggerui_blueprint)

# Define the scope for accessing Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_credentials():
    creds = None
    # Check if the token.json file exists
    current_dir = os.path.dirname(os.path.realpath(__file__))
    token_file_path = os.path.join(current_dir, 'token.json')
    if os.path.exists(token_file_path):
        # Load credentials from the token.json file
        creds = Credentials.from_authorized_user_file(token_file_path)
    # If credentials are missing or invalid
    if not creds or not creds.valid:
        # If credentials are expired and can be refreshed
        if creds and creds.expired and creds.refresh_token:
            # Refresh the credentials
            creds.refresh(Request())
        else:
            # Path to the credentials file
            credentials_file = os.path.join(current_dir, 'credentials.json')
            # Create a flow to obtain new credentials using the credentials file and defined scopes
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            # Run the flow to obtain new credentials via local server authentication
            creds = flow.run_local_server(port=0)
        # Save the refreshed or new credentials to token.json
        with open(token_file_path, 'w') as token:
            token.write(creds.to_json())
    return creds

def send_email(to, subject, message):
    # Get credentials
    creds = get_credentials()
    # Build the Gmail service
    service = build('gmail', 'v1', credentials=creds)
    # Create a raw email message
    raw_message = create_message(to, subject, message)
    # Send the email message and return whether it was successful
    return send_message(service, 'me', raw_message)

def create_message(to, subject, message_text):
    # Create a MIMEText object for the email message
    message = MIMEText(message_text)
    # Set the 'to', 'from', and 'subject' headers of the email message
    message['to'] = to
    message['from'] = 'onzecordmail@gmail.com'  # Hardcoded sender email address
    message['subject'] = subject
    # Encode the message as a raw string and return it
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    try:
        # Send the email message using the Gmail API and obtain the message ID
        message = service.users().messages().send(userId=user_id, body=message).execute()
        # Print the message ID indicating successful email delivery
        return True
    except Exception as e:
        # Print any errors that occur during the email sending process
        print('An error occurred: %s' % e)
        return False
    
# New route to handle browser requests for the index.html landing page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_email', methods=['POST'])
def send_email_api():
    # Extract email parameters from request
    to = request.json.get('to')
    subject = request.json.get('subject')
    message = request.json.get('message')

    # Log the received data
    app.logger.info('Received request: to=%s, subject=%s, message=%s', to, subject, message)
    
    # Send the email and check if it was successful
    success = send_email(to, subject, message)
    
    # Prepare response
    response = {'success': success}
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Run the Flask app in debug mode, listening on all network interfaces
