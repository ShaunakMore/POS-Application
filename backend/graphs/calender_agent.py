from __future__ import print_function
import datetime,os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from graphs.base_agent import make_response
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY")) #type:ignore
model = genai.GenerativeModel("gemini-2.0-flash") #type:ignore


SCOPES = ["https://www.googleapis.com/auth/calendar",
          "https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.send",
        ]

def _get_service():
  creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
  token_json = os.getenv("GOOGLE_TOKEN_JSON")

  if creds_json and token_json:
    try:
        creds_data = json.loads(token_json)
        creds = Credentials.from_authorized_user_info(creds_data, scopes=SCOPES)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            try:
              service = build("calendar", "v3", credentials=creds)
              return service
            except Exception as e:
              raise RuntimeError(f"Failed to build Google Calendar service: {e}")
        try:
          service = build("calendar", "v3", credentials=creds)
          return service
        except Exception as e:
          raise RuntimeError(f"Failed to build Google Calendar service: {e}")
    except Exception as e:
        print(f"[WARN] Failed to load Google credentials from env vars: {e}")

  

def _parse_event(prompt:str):
  """
  Use Gemini to create a clean, structured event object.
  """
  now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))  # Asia/Kolkata
  today_str = now.strftime("%Y-%m-%d %H:%M")
  prompt_text = f"""
  You are an assistant creating concise, human-friendly calendar events.
  
  Current local date and time: {today_str}

  Convert this user request into structured JSON:
  {{ "title": "", "date": "", "start_time": "", "end_time": ""}}

  Rules:
  - Title should be short and meaningful (e.g., "Meeting with Sarah" not "Schedule meeting with Sarah")
  - Date/time must be ISO 8601 where possible.
  - If times are missing, assume 1-hour duration starting in 1 hour from now.

  User request: "{prompt}"
  """
  try:
    result= model.generate_content(prompt_text)
    text = result.text.strip()
    start, end = text.find("{"), text.rfind("}") + 1
    data = json.loads(text[start:end])
  except Exception:
    now = datetime.datetime.now(datetime.timezone.utc)
    data = {
      "title": prompt.capitalize(),
      "date": now.date().isoformat(),
      "start_time": (now + datetime.timedelta(hours=1)).time().strftime("%H:%M"),
      "end_time": (now + datetime.timedelta(hours=2)).time().strftime("%H:%M"),
    }
  return data
  
  
def get_free_slots():
    service = _get_service()
    now = datetime.datetime.utcnow()
    tomorrow = now + datetime.timedelta(days=1)
    
    # Create timezone-aware datetimes or keep everything naive
    start = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0).isoformat() + 'Z'
    end = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 0).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId="primary",
        timeMin=start, timeMax=end,
        singleEvents=True, orderBy='startTime'
    ).execute()
    
    events = events_result.get("items", [])
    busy_slots = []
    
    for e in events:
        if "dateTime" in e["start"]:
            # Parse and strip timezone info to keep everything naive
            start_dt = datetime.datetime.fromisoformat(e["start"]["dateTime"].replace('Z', '+00:00')).replace(tzinfo=None)
            end_dt = datetime.datetime.fromisoformat(e["end"]["dateTime"].replace('Z', '+00:00')).replace(tzinfo=None)
            busy_slots.append((start_dt, end_dt))
    
    free_windows = []
    day_start = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)
    day_end = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 0)
    current_time = day_start
    
    for start_time, end_time in busy_slots:
        if current_time < start_time:
            free_windows.append((current_time.isoformat(), start_time.isoformat()))
        current_time = max(current_time, end_time)  # Handle overlapping events
    
    if current_time < day_end:
        free_windows.append((current_time.isoformat(), day_end.isoformat()))
    
    return free_windows


def get_busy_slots():
    service = _get_service()
    now = datetime.datetime.utcnow()
    tomorrow = now + datetime.timedelta(days=1)
    
    start = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0).isoformat() + 'Z'
    end = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 0).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId="primary",
        timeMin=start, timeMax=end,
        singleEvents=True, orderBy='startTime'
    ).execute()
    
    events = events_result.get("items", [])
    busy_windows = []
    
    for e in events:
        if "dateTime" in e["start"]:
            start_dt = datetime.datetime.fromisoformat(e["start"]["dateTime"].replace('Z', '+00:00')).replace(tzinfo=None)
            end_dt = datetime.datetime.fromisoformat(e["end"]["dateTime"].replace('Z', '+00:00')).replace(tzinfo=None)
            busy_windows.append((start_dt.isoformat(), end_dt.isoformat()))
            
    return busy_windows
      
def handle_calendar(prompt):
  """
  Parse simple natural-language scheduling and create an event
  """
  try:
    event_data = _parse_event(prompt)
    
    date = event_data.get("date")
    start_time = event_data.get("start_time", "10:00")
    end_time = event_data.get("end_time", "11:00")
    
    start_dt = datetime.datetime.fromisoformat(f"{date}T{start_time}")
    end_dt = datetime.datetime.fromisoformat(f"{date}T{end_time}")
    
    service = _get_service()
    
    event = {
      "summary": event_data["title"],
      "start": {"dateTime":start_dt.isoformat(), "timeZone": "Asia/Kolkata"},
      "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Kolkata"}
    }
    
    created = service.events().insert(calendarId="primary", body=event).execute()
    print("✅ Created event link:", created.get("htmlLink", "No link returned"))
    msg = (
      f"Event created:{event_data['title']}\n"
      f"Time: {start_time} - {end_time} UTC"
    )
    return make_response("CalendarAgent", True, msg, created)
  
  except Exception as e:
    return make_response("CalendarAgent", False, f"Failed to schedule {e}")
  
def get_all_events():
  service = _get_service()
  now = datetime.datetime.utcnow()
  tomorrow = now + datetime.timedelta(days=1)

  start = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0).isoformat() + 'Z'
  end = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 0).isoformat() + 'Z'

  events_result = service.events().list(
      calendarId="primary",
      timeMin=start,
      timeMax=end,
      singleEvents=True,
      orderBy="startTime"
  ).execute()

  events = events_result.get("items", [])
  busy_slots = []

  for e in events:
      start_time = e["start"].get("dateTime", e["start"].get("date"))
      end_time = e["end"].get("dateTime", e["end"].get("date"))
      summary = e.get("summary", "No Title")

      busy_slots.append({
          "summary": summary,
          "start_time": start_time,
          "end_time": end_time
      })

  return busy_slots
