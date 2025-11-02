"""Gmail OAuth2 Authentication Module."""

import os
import pickle
import base64
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

class GmailAPI:
    """Gmail API wrapper for OAuth2 authentication and operations."""

    def __init__(self, credentials_file='credentials.json', token_file='token.pickle'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.creds = None

    def authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None

        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        # If credentials were found, refresh if necessary and return service
        if creds:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())

            self.creds = creds
            self.service = build('gmail', 'v1', credentials=creds)
            return self.service

        # No saved credentials available — raise and let the app start the web OAuth flow
        raise FileNotFoundError(
            f"No saved token found ('{self.token_file}'). Start the OAuth web flow via the /gmail_auth route."
        )

    def get_authorization_url(self, redirect_uri):
        """Create an OAuth2 Flow for web application credentials and return the authorization URL and state.

        redirect_uri should be the full callback URL (example: https://yourhost/oauth2callback)
        """
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"Credentials file '{self.credentials_file}' not found.")

        # Ensure the redirect_uri we use matches one of the URIs registered
        # in the OAuth client (avoid redirect_uri_mismatch errors).
        try:
            with open(self.credentials_file, 'r', encoding='utf-8') as f:
                client_info = json.load(f)
            registered_redirects = []
            # client JSON may have a top-level 'web' or 'installed' key
            for key in ('web', 'installed'):
                if key in client_info and 'redirect_uris' in client_info[key]:
                    registered_redirects = client_info[key]['redirect_uris']
                    break
            # If the provided redirect_uri isn't registered, fall back to the first registered one
            if registered_redirects and redirect_uri not in registered_redirects:
                # prefer localhost style if possible, otherwise first available
                preferred = next((u for u in registered_redirects if 'localhost' in u), registered_redirects[0])
                redirect_uri = preferred
        except Exception:
            # If client file can't be parsed, continue with provided redirect_uri and let Flow handle errors
            pass

        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )

        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        return auth_url, state

    def fetch_token(self, authorization_response, state, redirect_uri):
        """Exchange the authorization response (full redirect URL) for credentials and save them.

        authorization_response should be the full URL that Google redirected back to (request.url)
        state should match the state stored when generating the auth URL
        redirect_uri is the callback URL used when generating the auth URL
        """
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"Credentials file '{self.credentials_file}' not found.")

        # Ensure the redirect_uri used here matches a registered URI in the client
        try:
            with open(self.credentials_file, 'r', encoding='utf-8') as f:
                client_info = json.load(f)
            registered_redirects = []
            for key in ('web', 'installed'):
                if key in client_info and 'redirect_uris' in client_info[key]:
                    registered_redirects = client_info[key]['redirect_uris']
                    break
            if registered_redirects and redirect_uri not in registered_redirects:
                preferred = next((u for u in registered_redirects if 'localhost' in u), registered_redirects[0])
                redirect_uri = preferred
        except Exception:
            pass

        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=SCOPES,
            state=state,
            redirect_uri=redirect_uri
        )

        # Exchange the authorization response for tokens
        flow.fetch_token(authorization_response=authorization_response)

        creds = flow.credentials

        # Save the credentials for the next run
        with open(self.token_file, 'wb') as token:
            pickle.dump(creds, token)

        self.creds = creds
        self.service = build('gmail', 'v1', credentials=creds)
        return self.service

    def get_messages(self, query='', max_results=100, label_ids=None):
        """Get messages matching the query."""
        if not self.service:
            self.authenticate()

        try:
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results,
                labelIds=label_ids
            ).execute()

            messages = result.get('messages', [])
            return messages
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def get_message_details(self, message_id):
        """Get detailed message information."""
        if not self.service:
            self.authenticate()

        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            return message
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def get_attachments(self, message_id):
        """Get all attachments from a message."""
        message = self.get_message_details(message_id)
        if not message:
            return []

        attachments = []
        payload = message['payload']

        # Process message parts
        parts = [payload] if 'parts' not in payload else payload['parts']

        for part in parts:
            if part.get('filename'):
                attachment_info = self._extract_attachment_info(part, message_id)
                if attachment_info:
                    attachments.append(attachment_info)

        return attachments

    def _extract_attachment_info(self, part, message_id):
        """Extract attachment information from message part."""
        filename = part.get('filename')
        if not filename:
            return None

        attachment_data = {
            'filename': filename,
            'mime_type': part.get('mimeType', 'application/octet-stream'),
            'size': part.get('body', {}).get('size', 0)
        }

        # Get attachment data
        if 'data' in part['body']:
            # Small attachment, data is included
            attachment_data['data'] = part['body']['data']
        elif 'attachmentId' in part['body']:
            # Large attachment, need to fetch separately
            attachment_id = part['body']['attachmentId']
            try:
                attachment = self.service.users().messages().attachments().get(
                    userId='me',
                    messageId=message_id,
                    id=attachment_id
                ).execute()
                attachment_data['data'] = attachment['data']
            except HttpError as error:
                print(f'Error fetching attachment: {error}')
                return None

        return attachment_data

    def download_attachment(self, attachment_data, save_path):
        """Download and save attachment to specified path."""
        try:
            file_data = base64.urlsafe_b64decode(
                attachment_data['data'].encode('UTF-8')
            )

            with open(save_path, 'wb') as f:
                f.write(file_data)

            return True
        except Exception as error:
            print(f'Error saving attachment: {error}')
            return False

    def search_messages_with_attachments(self, query='has:attachment', max_results=100):
        """Search for messages with attachments."""
        return self.get_messages(query=query, max_results=max_results)

    def get_message_headers(self, message):
        """Extract headers from message."""
        headers = {}
        if 'payload' in message and 'headers' in message['payload']:
            for header in message['payload']['headers']:
                headers[header['name'].lower()] = header['value']
        return headers

    def revoke_token(self):
        """Revoke the OAuth2 token and invalidate the access."""
        if not self.creds or not self.creds.refresh_token:
            # No token to revoke
            return True

        try:
            # Revoke the token using Google's revocation endpoint
            revoke_url = 'https://oauth2.googleapis.com/revoke'
            import requests
            response = requests.post(revoke_url, params={'token': self.creds.refresh_token})

            # Google returns 200 on success, 400 if token is invalid/expired
            if response.status_code in [200, 400]:
                # Clear local credentials
                self.creds = None
                self.service = None
                return True
            else:
                print(f"Token revocation failed with status: {response.status_code}")
                return False
        except Exception as error:
            print(f'Error revoking token: {error}')
            return False
