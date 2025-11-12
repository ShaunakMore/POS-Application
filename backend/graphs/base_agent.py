from typing import Dict, Any

def make_response(agent:str, success: bool, message:str, data: Dict[str, Any] = None): #type: ignore
  """
  Unified agent response format
  """
  return{
    "agent":agent,
    "success":success,
    "message": message,
    "data": data or {}
  }
  
  