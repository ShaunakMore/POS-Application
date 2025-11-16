import streamlit as st
import requests
from datetime import datetime
import time
import os

# Page configuration
st.set_page_config(
    page_title="POS - Personal Operating System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL
BACKEND_URL = st.secrets.get("BACKEND_URL")

# Custom CSS for dark mode aesthetic
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background-color: #0e1117;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #1e3a8a;
        margin-left: 20%;
        text-align: right;
    }
    .assistant-message {
        background-color: #374151;
        margin-right: 20%;
    }
    .timestamp {
        font-size: 0.7rem;
        color: #9ca3af;
        margin-top: 0.3rem;
    }
    .intent-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.7rem;
        margin-top: 0.3rem;
        background-color: #1f2937;
        color: #60a5fa;
    }
    .panel-card {
        background-color: #1f2937;
        padding: 1rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .task-item {
        background-color: #374151;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid;
    }
    .priority-high {
        border-left-color: #ef4444;
    }
    .priority-medium {
        border-left-color: #f59e0b;
    }
    .priority-low {
        border-left-color: #10b981;
    }
    .event-item {
        background-color: #374151;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #3b82f6;
    }
    .memory-item {
        background-color: #374151;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "memories" not in st.session_state:
    st.session_state.memories = []
if "events" not in st.session_state:
    st.session_state.events = []

# Helper functions
def fetch_tasks():
    """Fetch tasks from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/tasks", timeout=5)
        if response.status_code == 200:
            st.session_state.tasks = response.json()
            return True
    except Exception as e:
        st.error(f"❌ Failed to fetch tasks: {str(e)}")
    return False

def fetch_memories():
    """Fetch memories from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/memories", timeout=5)
        if response.status_code == 200:
            st.session_state.memories = response.json()
            return True
    except Exception as e:
        st.error(f"❌ Failed to fetch memories: {str(e)}")
    return False

def fetch_events():
    """Fetch calendar events from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/events", timeout=5)
        if response.status_code == 200:
            st.session_state.events = response.json()
            return True
    except Exception as e:
        st.error(f"❌ Failed to fetch events: {str(e)}")
    return False

def send_query(prompt):
    """Send query to backend and get response"""
    try:
        response =  requests.post(
            f"{BACKEND_URL}/query",
            json={"prompt": prompt},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Backend error: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Failed to send query: {str(e)}")
    return None

# Sidebar navigation
with st.sidebar:
    st.title("🤖 POS")
    st.caption("Personal Operating System")
    
    page = st.radio(
        "Navigation",
        ["💬 Chat", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    if st.button("🔄 Refresh All Data", use_container_width=True):
        with st.spinner("Refreshing..."):
            fetch_tasks()
            fetch_memories()
            fetch_events()
        st.toast("✅ Data refreshed!")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.toast("🧹 Chat cleared!")
        st.rerun()
    
    # XP Progress Box
    st.markdown("### 📊 XP Progress")
    try:
        response = requests.get(f"{BACKEND_URL}/xp_info", timeout=5)
        if response.status_code == 200:
            xp_data = response.json().get("data", {})
            
            for role in ["Producer", "Administrator", "Entrepreneur", "Integrator"]:
                xp_value = xp_data.get(role, 0)
                st.caption(role)
                st.progress(min(xp_value / 1000, 1.0))  # Assuming max 1000 XP per role
                st.caption(f"{xp_value} XP")
        else:
            st.caption("XP data unavailable")
    except Exception as e:
        st.caption("XP data unavailable")

# Main content based on page selection
if page == "💬 Chat":
    # Header
    st.title("🤖 POS — Personal Operating System")
    st.caption("Your AI-powered productivity assistant")
    
    # Main layout: Chat (70%) + Panels (30%)
    col1, col2 = st.columns([7, 3])
    
    with col1:
        st.subheader("💬 Chat with Martin")
        
        # Chat container
        chat_container = st.container(height=500)
        
        with chat_container:
            for message in st.session_state.messages:
                role = message["role"]
                content = message["content"]
                timestamp = message.get("timestamp", "")
                intent = message.get("intent", "")
                
                if role == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div>🧑 <strong>You</strong></div>
                        <div>{content}</div>
                        <div class="timestamp">{timestamp}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    agent = message.get("agent", "")
                    agent_emoji = "🔥" if agent == "TaskAgent" else "📊" if agent == "CalendarAgent" else "💫" if agent == "ReportAgent" else "🧠" if agent == "MemoryAgent" else "🤖"
                    intent_badge = f'<span class="intent-badge">{intent}</span>' if intent else ""
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div>{agent_emoji} <strong>Martin</strong></div>
                        <div>{content}</div>
                        {intent_badge}
                        <div class="timestamp">{timestamp}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        user_input = st.chat_input("Ask Martin anything...")
        
        if user_input:
            # Add user message
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": timestamp
            })
            
            # Send to backend
            with st.spinner("🤖 Martin is thinking..."):
                response_data = send_query(user_input)
            
            if response_data:
                # Backend returns "message" not "response"
                assistant_response =  response_data.get("message", response_data.get("response", "No response received"))
                intent = response_data.get("intent", "")
                agent = response_data.get("agent", "")
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "intent": intent,
                    "agent": agent
                })
                
                # Show toasts for specific intents
                if "task" in intent.lower():
                    st.toast("✅ Task operation completed")
                elif "calendar" in intent.lower():
                    st.toast("📅 Calendar operation completed")
                elif "memory" in intent.lower():
                    st.toast("🧠 Memory saved")
                
                # Refresh relevant data
                if "task" in intent.lower():
                    fetch_tasks()
                if "calendar" in intent.lower():
                    fetch_events()
                if "memory" in intent.lower():
                    fetch_memories()
            
                st.rerun()
    
    with col2:
        # Tasks Panel
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        col_title, col_refresh = st.columns([4, 1])
        with col_title:
            st.subheader("📋 Tasks")
        with col_refresh:
            if st.button("🔄", key="refresh_tasks", help="Refresh tasks"):
                fetch_tasks()
                st.toast("✅ Tasks refreshed")
                st.rerun()
        
        if not st.session_state.tasks:
            fetch_tasks()
        
        if st.session_state.tasks.get("tasks"):
            # Handle both nested and flat response structures
            tasks_list = st.session_state.tasks.get("tasks", st.session_state.tasks) if isinstance(st.session_state.tasks, dict) else st.session_state.tasks
            
            # Group by priority
            high_tasks = [t for t in tasks_list if t.get("priority") == "High"]
            medium_tasks = [t for t in tasks_list if t.get("priority") == "Medium"]
            low_tasks = [t for t in tasks_list if t.get("priority") == "Low"]
            
            for priority, tasks, css_class in [
                ("🔴 High Priority", high_tasks, "priority-high"),
                ("🟡 Medium Priority", medium_tasks, "priority-medium"),
                ("🟢 Low Priority", low_tasks, "priority-low")
            ]:
                if tasks:
                    st.caption(priority)
                    for task in tasks:
                        task_name = task.get("name", "Untitled Task")
                        xp = task.get("xp", 0)
                        st.markdown(f"""
                        <div class="task-item {css_class}">
                            <strong>{task_name}</strong>
                            {f'<div style="font-size: 0.8rem; color: #9ca3af;">XP: {xp}</div>' if xp else ''}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No tasks available")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Events Panel
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        col_title, col_refresh = st.columns([4, 1])
        with col_title:
            st.subheader("📅 Events")
        with col_refresh:
            if st.button("🔄", key="refresh_events", help="Refresh events"):
                fetch_events()
                st.toast("✅ Events refreshed")
                st.rerun()
        
        if not st.session_state.events:
            fetch_events()
        
        if st.session_state.events.get("events"):
            # Handle both nested and flat response structures
            events_list = st.session_state.events.get("events", st.session_state.events) if isinstance(st.session_state.events, dict) else st.session_state.events
            
            for event in events_list[:5]:
                title = event.get("title", event.get("summary", "Untitled Event"))
                time_str = event.get("time", event.get("start", ""))
                date_str = event.get("date", "")
                st.markdown(f"""
                <div class="event-item">
                    <strong>{title}</strong>
                    <div style="font-size: 0.8rem; color: #9ca3af;">{date_str} {time_str}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No upcoming events")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Memory Panel
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        col_title, col_refresh = st.columns([4, 1])
        with col_title:
            st.subheader("🧠 Memory")
        with col_refresh:
            if st.button("🔄", key="refresh_memory", help="Refresh memory"):
                fetch_memories()
                st.toast("✅ Memory refreshed")
                st.rerun()
        
        memory_search = st.text_input("🔍 Filter memories", key="memory_search")
        
        if not st.session_state.memories:
            fetch_memories()
        
        if st.session_state.memories:
            # Handle both nested and flat response structures
            memories_list = st.session_state.memories.get("memories")
            filtered_memories = memories_list
            if memory_search:
                filtered_memories = [
                    m for m in memories_list 
                    if memory_search.lower() in str(m).lower()
                ]
            
            for memory in filtered_memories:
                content = memory
                mem_type =  "general"
                st.markdown(f"""
                <div class="memory-item">
                    <div style="font-size: 0.7rem; color: #60a5fa;">{mem_type}</div>
                    <div style="font-size: 0.9rem;">{content}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No memories stored yet")
        
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "⚙️ Settings":
    st.title("⚙️ System Settings")
    
    st.subheader("🔌 Connected Services")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="panel-card">
            <h4>📝 Notion</h4>
            <p style="color: #10b981;">✅ Connected</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="panel-card">
            <h4>📅 Google Calendar</h4>
            <p style="color: #10b981;">✅ Connected</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="panel-card">
            <h4>🧠 ChromaDB</h4>
            <p style="color: #10b981;">✅ Connected</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("🤖 AI Model Info")
    st.markdown("""
    <div class="panel-card">
        <p><strong>Model:</strong> Gemini 2.0 Flash Lite</p>
        <p><strong>Provider:</strong> Google AI</p>
        <p><strong>Backend:</strong> FastAPI + LangGraph</p>
        <p><strong>Version:</strong> 1.0.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("🛠️ Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Chat History", use_container_width=True):
            st.session_state.messages = []
            st.success("Chat history cleared!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset All Data", use_container_width=True):
            st.session_state.tasks = []
            st.session_state.memories = []
            st.session_state.events = []
            st.success("All data reset!")
            st.rerun()
    
    st.divider()
    
    st.subheader("📊 Session Stats")
    st.markdown(f"""
    <div class="panel-card">
        <p><strong>Messages Sent:</strong> {len([m for m in st.session_state.messages if m['role'] == 'user'])}</p>
        <p><strong>Total Tasks:</strong> {len(st.session_state.tasks)}</p>
        <p><strong>Stored Memories:</strong> {len(st.session_state.memories)}</p>
        <p><strong>Upcoming Events:</strong> {len(st.session_state.events)}</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("🤖 POS — Personal Operating System | Powered by Gemini 2.0 Flash Lite")