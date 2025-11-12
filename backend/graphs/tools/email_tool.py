from langchain_core.tools import tool
from graphs.email_agent import send_email, read_email

@tool
def email_tool(action: str = "send", to: str = "", subject: str = "", body: str = "", query: str = "", max_results: int = 5) ->str:
  """
    Manage Gmail emails. 
    Remember to search in memory if user has mentioned someone's emil address before if email address has not been provided expicitly.

    Actions:
      - "send": Send an email
      - "read": Read emails matching a query

    Args:
      to: recipient email (for send)
      subject: subject line (for send)
      body: message content (for send)
      query: search query (for read)
      max_results: number of emails to fetch (for read)
    """
  if action == "send":
      return send_email(to, subject, body)
  if action == "read":
      return read_email(query, max_results)
  return "❌ Invalid action. Use 'send' or 'read'."