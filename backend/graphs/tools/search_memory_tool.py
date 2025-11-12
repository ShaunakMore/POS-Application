from langchain_core.tools import tool
from memory.vector_memory import VectorMemory

memory = VectorMemory()
@tool
def search_memory_tool(query: str, k: int = 3) -> str:
    """
    Search through past memories to recall relevant information.
    Use this when you need to remember what the user told you beforeand when you want to schedule something but need to take
    into consideration users daily activites or what user loves to do daily at certain point in the day.
    
    Args:
        query: What to search for (e.g., "user's coffee preferences","user's walk preferences")
        k: Number of memories to retrieve (default: 3)
    
    Returns:
        Relevant past memories
    """
    try:
        results = memory.search_memory(query, k=k)
        if not results:
            return "No relevant memories found."
        
        memories = "\n\n".join([f"- {r}" for r in results])
        return f"Found {len(results)} relevant memories:\n{memories}"
    except Exception as e:
        return f"❌ Memory search failed: {str(e)}"