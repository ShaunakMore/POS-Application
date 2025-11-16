from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.graphs.pos_graph import compiled as pos_graph
from backend.graphs.calender_agent import get_all_events
from backend.graphs.memory_agent import previous_convos
from backend.integrations.notion_client import get_pending_tasks
from backend.graphs.report_agent import handle_report
from backend.memory.pinecone_db import add_previous_convos, get_all_long_term_mems
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = FastAPI(title="POS API", version="2.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini for persona styling
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
conversational_history = []

# Persona definitions
PERSONAS = {
    "TaskAgent": "🔥 Producer — assertive, focused, and results-driven. Respond like a pragmatic motivator.",
    "CalendarAgent": "📊 Administrator — precise, structured, and efficient. Respond like an organized assistant.",
    "ReportAgent": "💫 Integrator — calm, reflective, and supportive. Respond with empathy and balance.",
    "MemoryAgent": "🧠 Memory keeper — thoughtful and observant. Respond with wisdom from past interactions.",
    "default": "🤖 Neutral assistant — clear, helpful, and professional tone."
}


def detect_agent_from_response(response: str, tool_calls: list) -> str:
    """
    Detect which agent/persona to use based on tool calls or response content.
    """
    if not tool_calls:
        return "default"
    
    tool_to_agent = {
        "task_tool": "TaskAgent",
        "create_task": "TaskAgent",
        "calendar_tool": "CalendarAgent",
        "create_calendar_event": "CalendarAgent",
        "report_tool": "ReportAgent",
        "add_memory_tool": "MemoryAgent",
        "search_memory_tool": "MemoryAgent"
    }
    
    last_tool = tool_calls[-1].get("tool", "")
    return tool_to_agent.get(last_tool, "default")


def apply_persona_styling(response: str, agent: str) -> str:
    """
    Apply persona-based styling to the response using Gemini.
    """
    persona_instruction = PERSONAS.get(agent, PERSONAS["default"])
    
    try:
        styled = model.generate_content(
            f"""
            Rewrite this assistant response in the tone of {persona_instruction}.
            keep it concise, natural, and conversational and don't lose any important details from the response.
            Use plain text only - no bold, italics, or special formatting.
            
            Response to rewrite:
            {response}
            """
        )
        
        return styled.text.strip()
    except Exception as e:
        return response  


@app.post("/query")
async def query_pos(prompt: str = Body(..., embed=True)):
    """
    Main query endpoint - processes user input through LangGraph.
    """
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    global conversational_history
    try:
        if len(conversational_history) >= 50: 
            conversational_history = conversational_history[-5:]
            to_add = "\n\n".join(conversational_history)
            add_previous_convos(to_add)
        # Execute the LangGraph
        prev = conversational_history[-5:]
        history = "\n\n".join(prev)
        result = pos_graph.invoke({"prompt": prompt,"memory":history})

        conversational_history.append(f"User:{result["prompt"]}\n Response: {result["response"]}")
        
        # Extract response and metadata
        base_response = result.get("response", "I couldn't process that request.")
        tool_calls = result.get("tool_calls", [])
        intent = result.get("intent", "unknown")
        error = result.get("error")
        
        if error:
            return {
                "message": f"I encountered an issue: {error}",
                "intent": "error",
                "tool_calls": []
            }
        
        # Detect which agent persona to use
        agent = detect_agent_from_response(base_response, tool_calls)
        
        return {
            "message": styled_response,
            "intent": intent,
            "agent": agent,
            "tool_calls": [tc.get("tool") for tc in tool_calls],
            "raw_response": base_response
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )

@app.get("/tasks")
async def get_tasks():
    """
    Get all tasks from Notion database.
    """
    try:
        tasks = get_pending_tasks()
        return {
            "tasks": tasks,
            "count": len(tasks)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch tasks: {str(e)}"
        )

@app.get("/events")
async def get_events():
    """
    Get all events in 24 hrs from Google Calender.
    """
    try:
        events = get_all_events()
        return {
            "events": events,
            "count": len(events)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch events: {str(e)}"
        )

@app.get("/memories")
async def get_memories():
    """
    Get all memories in the vectorDB
    """
    try:
        memories = get_all_long_term_mems()
        return {
            "memories": memories 
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch memories: {str(e)}"
        )

@app.get("/report")
async def get_report():
    """
    Generate a comprehensive productivity report.
    """
    try:
        result = handle_report()
        
        if isinstance(result, dict):
            message = result.get("message", "Report generated")
            
            return {
                "message": message,
                "success": result.get("success", True),
                "data": result.get("data", {})
            }
        
        return {"message": str(result)}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )

@app.get("/xp_info")
async def get_xp():
    with open("backend/data/xp_memory.json","r") as f:
       xp_data = json.load(f)
    return {"data":xp_data}

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "version": "2.0",
        "framework": "LangGraph"
    }
    
@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    """
    Root endpoint with API info.
    """
    return {
        "name": "POS API",
        "version": "2.0",
        "framework": "LangGraph + FastAPI",
        "endpoints": {
            "POST /query": "Process user queries through LangGraph",
            "GET /tasks": "Get all tasks from Notion",
            "GET /report": "Generate productivity report",
            "GET /health": "Health check"
        }
    }
