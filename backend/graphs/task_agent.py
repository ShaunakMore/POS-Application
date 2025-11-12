from integrations.notion_client import add_task_to_notion
from graphs.base_agent import make_response
from graphs.xp_agent import handle_xp_estimation
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import datetime

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def _parse_task(prompt: str) -> dict:
    """
    Use Gemini to interpret the user input and extract clean task metadata
    """
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    today_str = now.strftime("%Y-%m-%d %H:%M")
    
    prompt_text = f"""
    You are a smart productivity assistant analyzing task requests.
    
    Current date/time (Asia/Kolkata): {today_str}
    
    Extract structured task data from this request:
    "{prompt}"
    
    Respond ONLY with valid JSON (no markdown, no backticks):
    {{
      "task": "short title (max 6 words)",
      "priority": "High|Medium|Low",
      "avatar": "Producer|Administrator|Entrepreneur|Integrator",
      "suggested_time": "HH:MM-HH:MM format"
    }}
    
    Avatar guide:
    - Producer: Creative/building tasks (coding, writing, designing)
    - Administrator: Organizing, planning, managing
    - Entrepreneur: Strategic, business, networking
    - Integrator: Collaboration, communication, team tasks
    """
    
    try:
        result = model.generate_content(prompt_text)
        text = result.text.strip()
        
        # Extract JSON from response
        start = text.find("{")
        end = text.rfind("}") + 1
        
        if start == -1 or end == 0:
            raise ValueError("No JSON found in response")
        
        data = json.loads(text[start:end])
        
        # Validate required fields
        required = ["task", "priority", "avatar", "suggested_time"]
        if not all(k in data for k in required):
            raise ValueError("Missing required fields")
        
        # Validate priority
        if data["priority"] not in ["High", "Medium", "Low"]:
            data["priority"] = "Medium"
        
        # Validate avatar
        valid_avatars = ["Producer", "Administrator", "Entrepreneur", "Integrator"]
        if data["avatar"] not in valid_avatars:
            data["avatar"] = "Producer"
        
        return data
        
    except Exception as e:
        # Fallback with sensible defaults
        return {
            "task": prompt[:50].capitalize(),
            "priority": "Medium",
            "avatar": "Producer",
            "suggested_time": "14:00–15:00",
        }


def handle_tasks(prompt: str):
    """
    Handles task creation and XP estimation together.
    Returns a formatted response for the user.
    """
    try:
        
        parsed = _parse_task(prompt)
        
        
        xp_result = handle_xp_estimation(parsed)
        xp_value = xp_result.get("xp_assigned", 10) if isinstance(xp_result, dict) else 10
        parsed["xp"] = xp_value
        
        
        
        notion_result = add_task_to_notion(parsed)
        
       
        msg = (
            f"✅ Task created successfully!\n\n"
            f"📝 Task: {parsed['task']}\n"
            f"🎯 Priority: {parsed['priority']}\n"
            f"👤 Avatar: {parsed['avatar']}\n"
            f"⏰ Suggested Time: {parsed['suggested_time']}\n"
            f"⭐ XP Reward: {parsed['xp']}"
        )
        
        return make_response("TaskAgent", True, msg, {
            **notion_result,
            "parsed_task": parsed
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return make_response(
            "TaskAgent", 
            False, 
            f"❌ Failed to create task: {str(e)}"
        )
    