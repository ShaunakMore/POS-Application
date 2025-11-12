from __future__ import print_function
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
from email.mime.text import MIMEText
import json
import base64

load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/calendar",
          "https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.send",
        ]


def _get_service():
  creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
  token_json = os.getenv("GOOGLE_TOKEN_JSON")

  if creds_json and token_json:
      try:
          # Load both JSONs
          creds_data = json.loads(token_json)
          creds = Credentials.from_authorized_user_info(creds_data, scopes=SCOPES)

          # Refresh token if expired
          if creds and creds.expired and creds.refresh_token:
              creds.refresh(Request())
              try:
                service = build("gmail","v1",credentials=creds)
                return service
              except Exception as e:
                raise RuntimeError(f"Failed to build Google Calendar service: {e}")
          try:
            service = build("gmail","v1",credentials=creds)
            return service
          except Exception as e:
            raise RuntimeError(f"Failed to build Google Calendar service: {e}")
      except Exception as e:
          print(f"[WARN] Failed to load Google credentials from env vars: {e}")

def send_email(to: str, subject: str, body: str):
  try:
    service = _get_service()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
      userId ="me",body ={"raw": raw_message}
    ).execute()
    
    return f"Email sent to {to} with subject{subject}"
  except Exception as e:
    return f"Could not send email. Error - {e}"

def read_email(query: str, max_results: int = 3):
  try:
    service = _get_service()
    results = service.users().messages().list(
      userId = "me", q = query, maxResults = max_results
    ).execute()
    messages = results.get("messages",[])
    
    if not messages:
      return "No matching emails found"
    
    summaries = []
    for msg in messages:
      msg_data = service.users().messages().get(
        userId="me",id=msg["id"]
      ).execute()
      
      headers = msg_data["payload"]["headers"]
      subject = next(
        (h["value"] for h in headers if h["name"]== "Subject"),"(no subject)"
      )
      sender = next(
        (h["value"] for h in headers if h["name"]=="From"), "(unknown sender)"
      )
      snippet = msg_data.get("snippet","")[:100]
      summaries.append(f"From: {sender}\n Subject: {subject}\n Snippet:{snippet}")
      
    return "\n\n".join(summaries)
  except Exception as e:
    print(f"Could not read emails. Error - {e}")
    return f"Could not read emails. Error - {e}"

