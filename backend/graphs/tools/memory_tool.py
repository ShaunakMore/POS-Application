from langchain_core.tools import tool
from memory.pinecone_db import add_memory
from datetime import datetime

@tool
def add_memory_tool(entry: str, mem_type: str = "conversation") -> str:
    """
    Store a memory entry in Chroma vector database for later retrieval.
    Use this to save important information the user shares (preferences, facts, goals, tasks).
    
    Args:
        entry: The information to remember (e.g., "User likes coffee in the morning")
        mem_type: Type of memory - "conversation", "preference", "task", or "episodic"
    
    Returns:
        Confirmation message that memory was saved
    """
    try:
        timestamp = datetime.now().isoformat()
        formatted = f"[{mem_type.upper()} @ {timestamp}]\n{entry}"
        add_memory(formatted, mem_type)
        return f"✅ Memory saved: {entry[:50]}... (type: {mem_type})"
    except Exception as e:
        return f"❌ Failed to save memory: {str(e)}"
