import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY")) #type: ignore
model = genai.GenerativeModel("gemini-2.0-flash") #type: ignore

XP_FILE = "data/xp_memory.json"

def load_xp_memory():
  if not os.path.exists(XP_FILE):
    return {"Producer": 0, "Administrator": 0, "Entrepreneur": 0, "Integrator": 0}
  with open(XP_FILE, "r") as f:
    return json.load(f)
  
def save_xp_memory(xp_data):
  with open(XP_FILE, "w") as f:
    json.dump(xp_data, f , indent=2)
    
def handle_xp_estimation(task_data):
  """
  Calculates XP for a task using Gemini's judgement
  """
  try:
    xp_data = load_xp_memory()
    avatar = task_data.get("avatar","Producer")
    task_name = task_data.get("task","")
    priority = task_data.get("priority","Medium")
    
    context = f"""
    You are a motivational productivity assistant.
    The user has completed this task:
    Task: "{task_name}"
    Avatar: {avatar}
    Priority: {priority}
    
    Current XP balance:
    {json.dumps(xp_data, indent=2)}
    
    Estimate how much XP this task *should be worth* when completed
      Use these guidelines:
        - Low priority: 5–10 XP
        - Medium: 10–20 XP
        - High: 20–30 XP
        - If the avatar has much less XP than others, boost its XP slightly to motivate balance.

        Return JSON like: {{ "xp_assigned": 15, "reason": "High priority and underrepresented avatar." }}
    """
    
    result = model.generate_content(context)
    text = result.text.strip()
    start, end = text.find("{"), text.rfind("}") + 1
    clean_json = text[start:end]
    data = json.loads(clean_json)
    data.setdefault("xp_assigned",10)
    data.setdefault("reason","Balanced reward")
    xp_data[avatar] = xp_data[avatar] + data["xp_assigned"]
    save_xp_memory(xp_data)
    return data
  
  except Exception as e:
    print("⚠️ XP Estimation failed", e)
    return {"xp_assigned": 10, "reason": "Default XP assigned."}