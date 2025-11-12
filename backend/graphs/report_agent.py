from integrations.notion_client import get_all_tasks
from datetime import datetime
from graphs.base_agent import make_response

def handle_report():
    """
    Generates a comprehensive task report with stats and XP breakdown.
    """
    try:
        tasks = get_all_tasks()
        
        if not tasks:
            return make_response(
                "ReportAgent", 
                True, 
                "📊 No tasks found in your Notion database yet. Create your first task to get started!"
            )
        
        total = len(tasks)
        done = [t for t in tasks if t.get("status", "").lower() == "completed"]
        pending = total - len(done)
        completion_rate = (len(done) / total * 100) if total > 0 else 0
        
        # Calculate XP by avatar
        avatars = {}
        total_xp = 0
        for t in tasks:
            avatar = t.get("avatar") or "Unknown"
            xp = t.get("xp") or 0
            avatars[avatar] = avatars.get(avatar, 0) + xp
            total_xp += xp
        
        # Calculate XP earned from completed tasks
        earned_xp = sum(t.get("xp", 0) for t in done)
        
        # Priority breakdown
        priorities = {"High": 0, "Medium": 0, "Low": 0}
        for t in tasks:
            priority = t.get("priority", "Medium")
            if priority in priorities:
                priorities[priority] += 1
        
        # Format avatar breakdown
        avatar_breakdown = "\n".join([
            f"  • {avatar}: {xp} XP" 
            for avatar, xp in sorted(avatars.items(), key=lambda x: x[1], reverse=True)
        ])
        
        # Build comprehensive report
        msg = (
            f"📊 **Productivity Report** - {datetime.now().strftime('%B %d, %Y')}\n\n"
            f"📝 **Task Overview:**\n"
            f"  • Total Tasks: {total}\n"
            f"  • Completed: {len(done)} ({completion_rate:.1f}%)\n"
            f"  • Pending: {pending}\n\n"
            f"🎯 **Priority Breakdown:**\n"
            f"  • High: {priorities['High']}\n"
            f"  • Medium: {priorities['Medium']}\n"
            f"  • Low: {priorities['Low']}\n\n"
            f"⭐ **XP Statistics:**\n"
            f"  • Total Possible XP: {total_xp}\n"
            f"  • XP Earned: {earned_xp}\n"
            f"  • XP Remaining: {total_xp - earned_xp}\n\n"
            f"👤 **XP by Avatar:**\n{avatar_breakdown}"
        )
        
        return make_response("ReportAgent", True, msg, {
            "total_tasks": total,
            "completed": len(done),
            "pending": pending,
            "completion_rate": completion_rate,
            "total_xp": total_xp,
            "earned_xp": earned_xp,
            "avatars": avatars,
            "priorities": priorities
        })
        
    except Exception as e:
        print(f"❌ Report generation error: {e}")
        import traceback
        traceback.print_exc()
        
        return make_response(
            "ReportAgent", 
            False, 
            f"❌ Failed to generate report: {str(e)}"
        )