import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


# Configuration
SCOPES = ['https://www.googleapis.com/auth/blogger']
BLOG_ID = '51092151299805672'  # Found in your Blogger dashboard URL

def get_credentials():
    creds = None
    # token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('blogger_client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def create_post(title, content):
    creds = get_credentials()
    service = build('blogger', 'v3', credentials=creds)
    # Construct the post body
    body = {
        "kind": "blogger#post",
        "title": title,
        "content": content,  # Supports HTML tags
    }

    # Execute the insert request
    request = service.posts().insert(blogId=BLOG_ID, body=body, isDraft=False)
    response = request.execute()

    print(f"Post created! URL: {response.get('url')}")
