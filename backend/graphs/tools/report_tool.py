from langchain_core.tools import tool
from graphs.report_agent import handle_report

@tool
def report_tool() -> str:
    """
    Generates a comprehensive productivity report from Notion tasks.
    Use this when the user asks for a summary, report, progress update, or task statistics.
    
    The report includes:
    - Total tasks created
    - Completion rate and percentage
    - Pending tasks count
    - XP breakdown by avatar type
    - Current date context
    
    Returns:
        A formatted report with task statistics and completion metrics
    """
    try:
        result = handle_report()
        # Extract message from make_response dict
        if isinstance(result, dict):
            return result.get("message", str(result))
        return str(result)
    except Exception as e:
        return f"❌ Report generation failed: {str(e)}"