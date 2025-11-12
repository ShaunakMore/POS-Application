from langchain_core.tools import tool
from backend.graphs.task_agent import handle_tasks
from backend.integrations.notion_client import update_task, get_completed_tasks, get_pending_tasks

@tool
def task_tool(prompt: str= "", action:str = "add", task_name:str = "") -> str:
    """
        Handles task operations in Notion.

        Actions:
        - add: Parses `prompt` to create a new task with auto XP, priority, and avatar.
        - set_complete: Mark `task_name` as completed.
        - get_pending: Return all pending tasks.
        - get_completed: Return all completed tasks.

        Args:
        prompt: Task description (used only for 'add').
        action: One of {'add', 'set_complete', 'get_pending', 'get_completed'}.
        task_name: Task to update (used only for 'set_complete'), don't add task after the task name.

        Returns:
        A confirmation or list of tasks, else an error message.
    """
    if action.lower() == "add":
        try:
            result = handle_tasks(prompt)
            # If result is a dict from make_response, extract the message
            if isinstance(result, dict):
                return result.get("message", str(result))
            return str(result)
        except Exception as e:
            return f"❌ Task creation failed: {str(e)}"
        
    if action.lower() == "set_complete":
        print(f"\nSetting task:{task_name} as complete...")
        try:
            res = update_task(task_name)
            return res
        except Exception as e:
            return f"❌ Task updation failed: {str(e)}"
    
    if action.lower() == "get_pending":
        try:
            pending_tasks = get_pending_tasks()
            if pending_tasks == []:
                return "No pending tasks"
            return f",".join([task["name"] for task in pending_tasks])
        except Exception as e:
            return f"Could not get pending tasks {str(e)}"
    
    if action.lower() == "get_completed":
        try:
            completed_tasks = get_completed_tasks()
            if completed_tasks == []:
                return "No pending tasks"
            return f",".join([task["name"] for task in completed_tasks])
        except Exception as e:
            return f"Could not get completed tasks {str(e)}"
                