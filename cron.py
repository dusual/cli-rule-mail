import os.path

from db import *
from pony.orm import db_session
from datetime import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/gmail.labels']




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



def mark_as_read(service, message_id):
    message = service.users().messages().get(userId="me", id=message_id).execute()
    thread_id = message['threadId']
    thread_messages = service.users().threads().get(userId="me", id=thread_id).execute()
    thread_message_ids = [message['id'] for message in thread_messages["messages"]]
    for t_message_id in thread_message_ids:
        result = service.users().messages().modify(userId='me', id=t_message_id, body={
            'removeLabelIds': ['UNREAD']
         }).execute()



    return

def datetime_format_parse(date, format):
    try:
        date = datetime.strptime(date, format)
    except ValueError:
        return False

    return date




def mark_as_unread(service, message_id):
    message = service.users().messages().get(userId="me", id=message_id).execute()
    thread_id = message['threadId']
    thread_messages = service.users().threads().get(userId="me", id=thread_id).execute()
    thread_message_ids = [message['id'] for message in thread_messages["messages"]]
    for t_message_id in thread_message_ids:
        result = service.users().messages().modify(userId='me', id=t_message_id, body={
            'addLabelIds': ['UNREAD']
        }).execute()

    return


def move_message(service, message_id, folder):
    try:
        service.users().labels().create(userId="me", body={'name': folder}).execute()
    except Exception:
        pass
    labels = service.users().labels().list(userId="me").execute()
    labels = labels['labels']
    find_folder_label = [label for label in labels if label['name'] == folder]
    label = find_folder_label[0]
    result = service.users().messages().modify(userId='me', id=message_id, body={
        'addLabelIds': label['id']
    }).execute()

    return

def load_message(service, message_id):
    headers = service.users().messages().get(id=message_id, userId="me", format="full").execute()['payload']['headers']
    for header in headers:
        if header['name'] == "From":
            from_email = header['value']
        if header['name'] == 'To':
            to_email = header['value']
        if header['name'] == 'Date':
            date_unparsed = header['value']
        if header['name'] == 'Subject':
            subject = header['value']


    date = datetime_format_parse(date_unparsed, "%a, %d %b %Y %H:%M:%S %z")
    if not date:
        date = datetime_format_parse(date_unparsed, "%a, %d %b %Y %H:%M:%S %Z")

    if not date:
        print("Could not parse the date for this format")
        return

    with db_session:
        Message(
            gmail_id=message_id,
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            date=date
        )
    print(from_email, to_email, date, subject)


def fetch_message_ids(service):
    try:
        message_all = service.users().messages().list(userId='me').execute()
    except Exception(e):
        print("Error fetching Message list")

    messages = message_all['messages']
    message_ids = [entry['id'] for entry in messages]

    return message_ids


if __name__ == '__main__':
    service = authenticate()
    # TODO: this should be fetch more pages but for now letting it be single page for simplicity
    message_ids = fetch_message_ids(service)
    for message_id in message_ids:
        load_message(service, message_id=message_id)

