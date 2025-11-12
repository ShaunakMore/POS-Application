from notion_client import Client
import os
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.getenv("NOTION_TOKEN"))
NOTION_DB_ID = os.getenv("NOTION_TASK_DB")
NOTION_DATA_SOURCE_ID = os.getenv("NOTION_DATA_SOURCE_ID")

def add_task_to_notion(task_data):
  """
  Creates a new Notion Page (task) inside the POS Tasks database.
  task_data should contain: task, avatar, priority, suggested_time, status, xp
  """
  notion.pages.create(
    parent={"database_id":NOTION_DB_ID},
    properties={
      "Name":{"title":[{"text":{"content":task_data["task"]}}]},
      "Avatar":{"select":{"name":task_data.get("avatar","Producer")}},
      "Priority":{"select":{"name":task_data.get("priority","Medium")}},
      "Suggested Time":{"rich_text":[{"text":{"content":task_data.get("suggested_time","")}}]},
      "Status": {"select":{"name":task_data.get("status","Pending")}},
      "XP":{"number":task_data.get("xp",0)}
    },
  )
  return task_data

def get_all_tasks():
  """
  Fetch all current tasks from Notion
  """
  
  res = notion.data_sources.query(data_source_id=NOTION_DATA_SOURCE_ID) #type:ignore
  tasks = []
  for page in res["results"]: #type:ignore
    props = page["properties"]
    tasks.append({
      "id": page["id"],
      "name": props["Name"]["title"][0]["plain_text"] if props["Name"]["title"] else "",
      "avatar": props["Avatar"]["select"]["name"] if props["Avatar"]["select"] else "",
      "priority": props["Priority"]["select"]["name"] if props["Priority"]["select"] else "",
      "status": props["Status"]["select"]["name"] if props["Status"]["select"] else "",
      "suggested_time": props["Suggested Time"]["rich_text"][0]["plain_text"] if props["Suggested Time"]["rich_text"] else "",
      "xp": props["XP"]["number"] if props["XP"]["number"] else 0
    })
  
  return tasks

def get_completed_tasks():
  """
  Fetch completed tasks from Notion
  """
  
  res = notion.data_sources.query(data_source_id=NOTION_DATA_SOURCE_ID) #type:ignore
  tasks = []
  for page in res["results"]: #type:ignore
    props = page["properties"]
    if(props["Status"]["select"]["name"] == "Completed"):
      tasks.append({
        "id": page["id"],
        "name": props["Name"]["title"][0]["plain_text"] if props["Name"]["title"] else "",
        "avatar": props["Avatar"]["select"]["name"] if props["Avatar"]["select"] else "",
        "priority": props["Priority"]["select"]["name"] if props["Priority"]["select"] else "",
        "status": props["Status"]["select"]["name"] if props["Status"]["select"] else "",
        "xp": props["XP"]["number"] if props["XP"]["number"] else 0
      })
  
  return tasks

def get_pending_tasks():
  """
  Fetch completed tasks from Notion
  """
  
  res = notion.data_sources.query(data_source_id=NOTION_DATA_SOURCE_ID) #type:ignore
  tasks = []
  for page in res["results"]: #type:ignore
    props = page["properties"]
    if(props["Status"]["select"]["name"] == "Pending"):
      tasks.append({
        "id": page["id"],
        "name": props["Name"]["title"][0]["plain_text"] if props["Name"]["title"] else "",
        "avatar": props["Avatar"]["select"]["name"] if props["Avatar"]["select"] else "",
        "priority": props["Priority"]["select"]["name"] if props["Priority"]["select"] else "",
        "status": props["Status"]["select"]["name"] if props["Status"]["select"] else "",
        "xp": props["XP"]["number"] if props["XP"]["number"] else 0
      })
  
  return tasks

def update_task(task_name):
  print(f"\nUpdating {task_name}")
  try:
    response = response = notion.data_sources.query(
            data_source_id=NOTION_DATA_SOURCE_ID,
            filter={
                "property": "Name",
                "title": {  # Changed from "title": {"equals": task_name}
                    "equals": task_name  # This is the correct structure
                }
            }
        )
    results = response["results"]
    if results:
      page_id = results[0]["id"]
      if not page_id:
          return None

      notion.pages.update(
          page_id=page_id,
          properties={
              "Status": {"select": {"name": "Completed"}}
          }
      )
    return "Task Not Found"
  except Exception as e:
    return "Could not update task"