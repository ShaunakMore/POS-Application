import os,json
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

from graphs.tools.task_tool import task_tool
from graphs.tools.calendar_tool import calendar_tool
from graphs.tools.report_tool import report_tool
from graphs.tools.memory_tool import add_memory_tool
from graphs.tools.search_memory_tool import search_memory_tool
from graphs.tools.email_tool import email_tool

load_dotenv()

# Initialize LangChain's Gemini wrapper
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7
)

# Create React agent with all tools
agent = create_react_agent(
    llm,
    tools=[
        task_tool,           # Creates tasks in Notion with XP
        calendar_tool,       # Schedules events in Google Calendar
        report_tool,         # Generates productivity reports
        add_memory_tool,     # Stores memories in vector DB
        search_memory_tool,
        email_tool
    ]
)

def parent_node(state):
    """
    Parent reasoning node using LangGraph's React agent.
    The agent automatically decides which tools to call based on user input.
    """
    prompt = state.get("prompt", "")
    prev_memory = state.get("memory", "")

    reasoning_input = f"{prev_memory}\n\nUser: {prompt}"
    print(f"Previous convos:{reasoning_input}")
    if not prompt.strip():
        return {
            "intent": "error",
            "response": "No input provided",
            "error": "Empty prompt",
            "prompt": prompt
        }
    
    try:        
        additional_instructions = f"""
        Cater to the users rquest and use the tools given to you whenever needed to give the best possible answer to the user.
        Call multiple tools if needed to gather more context related to the user needs and give the best possible answer.
        """
        
        # Invoke agent - it handles tool calling automatically
        result = agent.invoke({"messages": [("user",  additional_instructions + reasoning_input)]})
        
        # Extract messages from result
        messages = result.get("messages", [])
        final_message = messages[-1] if messages else None
        response_text = final_message.content if final_message else "No response generated"
        
        # Track which tools were called
        tool_calls = []
        for msg in messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_calls.append({
                        "tool": tc.get("name"),
                        "args": tc.get("args")
                    })
        
        print(f"✅ Agent response generated")
        print(response_text)
        new_entry = f"USER: {prompt}\nASSISTANT: {response_text}"
        new_memory = prev_memory + "\n" + new_entry
        if tool_calls:
            print(f"🛠️  Tools called: {[tc['tool'] for tc in tool_calls]}")
        
        intent = "" 
        try: 
            start, end = final_message.content.find("{"),final_message.content.rfind("}") +1
            res_json = json.loads(final_message.content[start:end])
            intent = res_json["intent"]
        except Exception:
            intent = "direct_response"
        
        return {
            "intent": intent if intent else "direct_response",
            "response": response_text,
            "tool_calls": tool_calls,
            "messages": messages,
            "prompt": prompt,
            "memory": new_memory
        }
        
    except Exception as e:
        print(f"❌ parent_node error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "intent": "error",
            "error": str(e),
            "response": f"I encountered an error: {str(e)}",
            "prompt": prompt
        }