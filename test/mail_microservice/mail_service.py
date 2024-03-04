import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Get the path of the current directory
            current_dir = os.path.dirname(os.path.realpath(__file__))
            credentials_file = os.path.join(current_dir, 'credentials.json')
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def send_email(sender, to, subject, message):
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    raw_message = create_message(sender, to, subject, message)
    return send_message(service, 'me', raw_message)

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('Message Id: %s' % message['id'])
        return True
    except Exception as e:
        print('An error occurred: %s' % e)
        return False

if __name__ == '__main__':
    sender = 'onzecordmail@gmail.com'
    to = 'gallo.noah@gmail.com'
    subject = 'Test Email'
    message = 'This is a test email sent using OAuth2 authentication with Gmail API.'
    success = send_email(sender, to, subject, message)
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email.")
