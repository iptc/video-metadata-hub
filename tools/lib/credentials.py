#!/usr/bin/env python3
"""
Google Sheets API Credentials Management

Handles authentication for Google Sheets API access
"""

import os
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

from .constants import SCOPES


def get_client_secret_path():
    """
    Get the path to client_secret.json
    
    Looks in multiple locations in order:
    1. tools/client_secret.json
    2. tools/lib/client_secret.json
    3. Current directory
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.dirname(current_dir)
    
    locations = [
        os.path.join(tools_dir, 'client_secret.json'),
        os.path.join(current_dir, 'client_secret.json'),
        'client_secret.json'
    ]
    
    for path in locations:
        if os.path.exists(path):
            return path
    
    raise FileNotFoundError(
        "client_secret.json not found. Please download it from Google Cloud Console "
        "and place it in the tools/ directory."
    )


def get_token_path():
    """Get the path to store the token.json file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.dirname(current_dir)
    return os.path.join(tools_dir, 'token.json')


def get_credentials():
    """
    Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials: The obtained credential.
    """
    creds = None
    token_path = get_token_path()
    
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes=SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        refreshed = False
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                refreshed = True
            except RefreshError as e:
                # Refresh token was revoked or expired (common with OAuth
                # clients in "Testing" status, where refresh tokens expire
                # after 7 days). Fall through to the interactive flow.
                print(f"⚠ Stored refresh token rejected by Google ({e}).")
                print(f"  Discarding {token_path} and re-authenticating...")
                try:
                    os.remove(token_path)
                except OSError:
                    pass
                creds = None

        if not refreshed and not (creds and creds.valid):
            client_secret_path = get_client_secret_path()
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_path, scopes=SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds


if __name__ == '__main__':
    # Test credentials
    try:
        print("Testing Google Sheets API credentials...")
        creds = get_credentials()
        print("✓ Credentials obtained successfully")
    except Exception as e:
        print(f"✗ Error: {e}")

