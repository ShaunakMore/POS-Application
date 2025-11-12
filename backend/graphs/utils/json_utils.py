import json
import re

def extract_json(text: str, key: str = None):
    """
    Safely extract and parse JSON content from a model response string.
    Optionally return a specific key from that JSON.
    """
    if not text:
        return None

    # Try to locate the first and last braces
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return None

    json_str = match.group(0)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        return None

    if key:
        return data.get(key)
    return data
