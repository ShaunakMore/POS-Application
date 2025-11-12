from typing import TypedDict, List, Optional,Optional

class PosState(TypedDict, total=False):
    prompt: str
    intent: str
    response: str
    tool_calls: List[dict]
    memory: str
    messages: str
    memory_status: str
    error: Optional[str]