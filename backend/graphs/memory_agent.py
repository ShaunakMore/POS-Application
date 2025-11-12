from backend.memory.conversation_memory import ConversationMemory

short_term = ConversationMemory()

def previous_convos():
  convos = short_term.retrieve_all()
  formatted = "\n\n".join([f"{m['role'].upper()}: {d}" for d,m in convos])
  return formatted