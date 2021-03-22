import os.path

from db import *
from pony.orm import db_session
from datetime import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    if not os.path.exists('credentials.json'):
        print("Add credentials.json by Enabling the Gmail API")
        return

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        service = build('gmail', 'v1', credentials=creds)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('tokens.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


def load_message(service): #, message_id):
    headers = service.users().messages().get(id="1785499859b9a9cc", userId="me", format="full").execute()['payload']['headers']
    for header in headers:
        if header['name'] == "From":
            from_email = header['value']
        if header['name'] == 'To':
            to_email = header['value']
        if header['name'] == 'Date':
            date = header['value']
        if header['name'] == 'Subject':
            subject = header['value']

    date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
    with db_session:
        Message(
            gmail_id="1785499859b9a9cc",
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            date=date
        )
    print(from_email, to_email, date, subject)

#    import pdb; pdb.set_trace()
#    print(1)
#    with db_session:
#        Message(
#            gmail_id='abc',
#            from_email='test',
#            to_email='test123',
#            subject='tttt',
#        )

"""
def fetch_message_ids(service):
    try:
        message_all = service.users().messages().list(userId='me').execute()
    except Exception(e):
        print("Error fetching Message list")

    messages = message_all['messages']
    message_ids = [entry['id'] for entry in messages]
    return message_ids
"""

if __name__ == '__main__':
    service = authenticate()
    # TODO: this should be fetch more pages but for now letting it be single page for simplicity
    #message_ids = fetch_message_ids(service)
    #for message_id in message_ids:
    load_message(service)
    #load_message(service, message_id=message_id)
