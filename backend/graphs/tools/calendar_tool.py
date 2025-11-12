from langchain_core.tools import tool
from graphs.calender_agent import handle_calendar, get_free_slots, get_busy_slots

@tool
def calendar_tool(prompt: str,action: str = "add") -> str:
    """
    Use this tool to interact with the user's Google Calendar for scheduling and availability management.
    Remember to search in memory if user has mentioned their or someone's preferences if they have not been provided expicitly.
    Supports three primary actions:
    - **"add"**  →  Creates or schedules new calendar events or meetings based on the user's natural language input.
                    Example: "schedule a meeting with Sarah tomorrow at 3pm"
    - **"free"** →  Retrieves a list of upcoming free time slots from the user's calendar.
                    Returns start → end times for available windows.
    - **"busy"** →  Retrieves a list of upcoming busy or occupied slots from the user's calendar.
                    Returns start → end times for meetings or events already booked.

    Args:
        prompt (str): A natural language scheduling query or description of the event
                      (used mainly when `action="add"`).
        action (str): Determines which calendar function to perform. Accepts one of:
                      ["add", "free", "busy"]. Defaults to "add".

    Returns:
        str: A human-readable response indicating the result of the action:
             - Event creation summary (for add)
             - List of free slots (for free)
             - List of busy slots (for busy)
             - Or an error message if lookup fails.

    Example usage:
        calendar_tool("schedule a call with Alex at 5pm tomorrow", action="add")
        calendar_tool("", action="free")
        calendar_tool("", action="busy")
    """
    if action.lower() == "add":
        result = handle_calendar(prompt)
        return str(result)
    
    if action.lower() == "free":
        try:
            free_slots = get_free_slots()
            free_slots_str = "\n".join([f"{s[0]} → {s[1]}" for s in free_slots]) or "No free slots found."
            return free_slots_str
        except Exception as e:
            free_slots_str = f"Calendar lookup failed: {e}"
            return free_slots_str
    
    if action.lower() == "busy":
        try:
            busy_slots = get_busy_slots()
            busy_slots_str = "\n".join([f"{s[0]} → {s[1]}" for s in busy_slots]) or "No free slots found."
            return busy_slots_str
        except Exception as e:
            busy_slots_str = f"Calendar lookup failed: {e}"
            return busy_slots_str