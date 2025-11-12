from datetime import datetime
from memory.vector_memory import VectorMemory
from memory.conversation_memory import ConversationMemory

long_term = VectorMemory()
short_term = ConversationMemory()

def memory_node(state):
    prompt = state.get("prompt", "")
    response = state.get("response", "")
    intent = state.get("intent", "unknown")
    timestamp = datetime.now().isoformat()

    # 💬 Short-term: store conversation turns
    short_term.add_message("user", prompt)
    short_term.add_message("assistant", response)

    print(f"💬 updated short-term semantic memory")
    return {"memory_status": "Memory updated."}
