import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid

from app.schemas import DiscoverySessionState
from app.state import TopicTracker
from app.agent import DiscoveryAgent

app = FastAPI(title="CogniVerse AI Discovery Agent API", version="1.0")

sessions: Dict[str, Dict[str, Any]] = {}

tracker = TopicTracker()
agent = DiscoveryAgent()

class StartSessionResponse(BaseModel):
    session_id: str
    welcome_message: str
    current_topic: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    agent_message: str
    current_topic: str
    completed_topics: List[str]

def fallback_extraction(text: str, state: DiscoverySessionState):
    """استخراج محلي برمجياً لضمان عدم ضياع أي بيانات ومنع التكرار في القوائم"""
    text_lower = text.lower()
    
    # 1. المسمى الوظيفي
    if any(role in text_lower for role in ["manager", "lead", "head", "director"]):
        if not state.role_info.role_title:
            match = re.search(r'(?:i am|i\'m|as a)\s+([a-z\s]+manager|[a-z\s]+lead|[a-z\s]+director)', text_lower)
            state.role_info.role_title = match.group(1).title() if match else "Department Lead / Manager"

    # 2. الوقت المستغرق
    time_match = re.search(r'(\d+\s*(?:hours?|hrs?|mins?|minutes?)\s*(?:daily|per day|weekly)?)', text_lower)
    if time_match:
        state.primary_workflow.time_consumed = time_match.group(1)

    # 3. الأنظمة المستخدمة (بدون تكرار)
    known_systems = ["excel", "dms", "crm", "erp", "email", "sheets", "sap", "power bi", "legacy dms"]
    for sys in known_systems:
        if sys in text_lower:
            sys_name = sys.upper() if len(sys) <= 4 or sys == "legacy dms" else sys.title()
            if sys_name not in state.primary_workflow.systems_used:
                state.primary_workflow.systems_used.append(sys_name)

    # 4. المشاكل والعمليات (تأكيد منع التكرار)
    if any(keyword in text_lower for keyword in ["manual", "double-booking", "delay", "error"]):
        workaround_msg = "Manual data updates & error-prone tracking"
        if workaround_msg not in state.primary_workflow.workarounds:
            state.primary_workflow.workarounds.append(workaround_msg)

@app.post("/start", response_model=StartSessionResponse)
def start_session():
    session_id = str(uuid.uuid4())
    state = DiscoverySessionState()
    
    welcome_msg = (
        "Hello! I am your CogniVerse AI Discovery Consultant. "
        "I'm here to learn about your department's key processes, performance metrics, and system challenges "
        "so we can identify high-impact opportunities for automation and AI.\n\n"
        "To get started, could you please share your current role and responsibilities within the function?"
    )
    
    sessions[session_id] = {
        "state": state,
        "chat_history": [{"role": "assistant", "content": welcome_msg}]
    }
    
    return StartSessionResponse(
        session_id=session_id,
        welcome_message=welcome_msg,
        current_topic=state.current_topic
    )

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    state: DiscoverySessionState = session["state"]
    chat_history: list = session["chat_history"]
    
    chat_history.append({"role": "user", "content": request.message})
    
    # 1. استخراج عبر LLM
    extracted_data = agent.extract_structured_data(state, request.message)
    
    if isinstance(extracted_data, dict):
        if extracted_data.get("role_title"):
            state.role_info.role_title = str(extracted_data["role_title"])
            
        if extracted_data.get("tracked_kpis"):
            kpis = extracted_data["tracked_kpis"] if isinstance(extracted_data["tracked_kpis"], list) else [str(extracted_data["tracked_kpis"])]
            for kpi in kpis:
                if kpi and str(kpi) not in state.kpis.tracked_kpis:
                    state.kpis.tracked_kpis.append(str(kpi))
                
        if extracted_data.get("process_name"):
            state.primary_workflow.process_name = str(extracted_data["process_name"])
            
        if extracted_data.get("time_consumed"):
            state.primary_workflow.time_consumed = str(extracted_data["time_consumed"])
            
        if extracted_data.get("systems_used"):
            systems = extracted_data["systems_used"] if isinstance(extracted_data["systems_used"], list) else [str(extracted_data["systems_used"])]
            for sys in systems:
                if sys and str(sys) not in state.primary_workflow.systems_used:
                    state.primary_workflow.systems_used.append(str(sys))

        if extracted_data.get("workarounds"):
            workarounds = extracted_data["workarounds"] if isinstance(extracted_data["workarounds"], list) else [str(extracted_data["workarounds"])]
            for wa in workarounds:
                if wa and str(wa) not in state.primary_workflow.workarounds:
                    state.primary_workflow.workarounds.append(str(wa))

    # 2. تطبيق الـ Fallback لتصيّد أي شيء فات الـ LLM مع الضمان بعدم التكرار
    fallback_extraction(request.message, state)

    # 3. تحديث التقدم والموضوع الحلي
    state = tracker.update_state_progress(state, request.message)
    
    # 4. توليد رد المستشار الذكي
    agent_msg = agent.generate_response(state, chat_history)
    chat_history.append({"role": "assistant", "content": agent_msg})
    
    session["state"] = state
    session["chat_history"] = chat_history
    
    return ChatResponse(
        agent_message=agent_msg,
        current_topic=state.current_topic,
        completed_topics=state.completed_topics
    )

@app.get("/export/{session_id}")
def export_report(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state: DiscoverySessionState = sessions[session_id]["state"]
    return state.model_dump()