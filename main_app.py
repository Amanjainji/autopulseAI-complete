"""
AI-Powered Predictive Vehicle Maintenance System
Main application with FastAPI backend, Master Agent orchestration, and UEBA security
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import asyncio
import os
import uuid
import uvicorn
import base64
try:
    from jose import jwt as jose_jwt
    HAS_JOSE = True
except Exception:
    HAS_JOSE = False

# Import custom modules
from ueba_security import UEBAMonitor
from agents import (
    DataAnalysisAgent, 
    DiagnosisAgent, 
    CustomerEngagementAgent,
    SchedulingAgent,
    FeedbackAgent,
    ManufacturingInsightsAgent,
    MasterAgent
)
from chat_agent import ChatAIAgent
from voice_agent import VoiceAgent, VoiceIntentEvent, create_voice_router
from data_generator import VehicleDataGenerator
from config import SETTINGS

# Initialize FastAPI app
app = FastAPI(
    title="AI Predictive Vehicle Maintenance System",
    description="Agentic AI system for predictive maintenance with Master-Worker architecture and UEBA security",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://autopulse-ai-frontend.vercel.app/",  # your Vercel frontend domain
        "http://localhost:5173",                    # for local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === DATA STORAGE ===
CUSTOMERS: Dict = {}
VEHICLES: Dict = {}
SENSOR_DATA: Dict = {}
SERVICE_HISTORY: Dict = {}
PREDICTIONS: Dict = {}
APPOINTMENTS: Dict = {}

# Background task handles
_orchestration_task: Optional[asyncio.Task] = None
_telemetry_task: Optional[asyncio.Task] = None
_appointment_task: Optional[asyncio.Task] = None
_prediction_task: Optional[asyncio.Task] = None

# === INITIALIZE COMPONENTS ===
UEBA = UEBAMonitor()
Master = MasterAgent(UEBA)
ChatAgent = None  # Will be initialized after data loading
VoiceService: Optional[VoiceAgent] = None

# Register voice routing (voice agent attached during initialization)
app.include_router(create_voice_router(lambda: VoiceService))

# === AUTH SETTINGS (simple demo JWT) ===
SECRET_KEY = "autopulse-demo-secret-key"
ALGORITHM = "HS256"

# === PYDANTIC MODELS ===

class CustomerModel(BaseModel):
    id: str
    name: str
    phone: str
    email: str
    address: Optional[str] = ""
    purchase_date: str
    vehicle_id: str

class VehicleModel(BaseModel):
    id: str
    customer_id: str
    model: str
    model_number: str
    vin: Optional[str] = ""
    registration_number: Optional[str] = ""
    mileage: int = 0
    health_status: str = "good"

class ChatMessageModel(BaseModel):
    customer_id: str
    message: str

class ChatResponseModel(BaseModel):
    customer_id: str
    response: str
    timestamp: str

class TelemetryDataModel(BaseModel):
    vehicle_id: str
    engine_temp: float
    oil_pressure: float
    battery_voltage: float
    fuel_level: float

class AppointmentModel(BaseModel):
    vehicle_id: str
    customer_id: str
    service_type: str
    preferred_date: Optional[str] = None

class LoginModel(BaseModel):
    email: str
    password: str

# === INITIALIZATION FUNCTION ===

def initialize_system():
    """Initialize system with sample data and agents"""
    global ChatAgent, VoiceService
    
    print("\n" + "="*80)
    print("🚀 INITIALIZING AI PREDICTIVE MAINTENANCE SYSTEM")
    print("="*80 + "\n")
    
    # Generate sample vehicles
    print("📊 Generating synthetic vehicle data...")
    vehicles_data = VehicleDataGenerator.generate_sample_vehicles()
    
    for vehicle_data in vehicles_data:
        customer = vehicle_data["customer"]
        vehicle = vehicle_data["vehicle"]
        sensor = vehicle_data["sensor_data"]
        history = vehicle_data["service_history"]
        
        CUSTOMERS[customer["id"]] = customer
        VEHICLES[vehicle["id"]] = vehicle
        SENSOR_DATA[vehicle["id"]] = sensor
        
        for service in history:
            SERVICE_HISTORY[service["id"]] = service
    
    print(f"   ✅ Loaded {len(CUSTOMERS)} customers")
    print(f"   ✅ Loaded {len(VEHICLES)} vehicles")
    print(f"   ✅ Loaded {len(SENSOR_DATA)} sensor readings")
    print(f"   ✅ Loaded {len(SERVICE_HISTORY)} service records")
    
    # Initialize Chat Agent
    print("\n💬 Initializing Chat AI Agent...")
    ChatAgent = ChatAIAgent(CUSTOMERS, VEHICLES, SENSOR_DATA, PREDICTIONS, APPOINTMENTS, SERVICE_HISTORY)
    print("   ✅ Chat Agent ready")

    VoiceService = VoiceAgent(
        ueba=UEBA,
        base_url=os.getenv("VOICE_WEBHOOK_BASE_URL"),
        caller_id=os.getenv("TWILIO_CALLER_ID"),
        intent_callback=_handle_voice_intent,
    )
    print("   ✅ Voice Agent configured (provider: {} )".format("twilio" if VoiceService.twilio_enabled else "offline"))
    
    # Initialize and register worker agents
    print("\n🤖 Initializing Worker Agents...")
    
    Master.register_worker("DataAnalysis", DataAnalysisAgent(UEBA, VEHICLES, SENSOR_DATA, PREDICTIONS))
    Master.register_worker("Diagnosis", DiagnosisAgent(UEBA, VEHICLES, PREDICTIONS))
    Master.register_worker("CustomerEngagement", CustomerEngagementAgent(UEBA, CUSTOMERS, VEHICLES, PREDICTIONS, voice_agent=VoiceService))
    Master.register_worker("Scheduling", SchedulingAgent(UEBA, CUSTOMERS, VEHICLES, PREDICTIONS, APPOINTMENTS))
    Master.register_worker("Feedback", FeedbackAgent(UEBA, CUSTOMERS, VEHICLES, SERVICE_HISTORY))
    Master.register_worker("ManufacturingInsights", ManufacturingInsightsAgent(UEBA, VEHICLES, PREDICTIONS))
    
    print("\n" + "="*80)
    print("✅ SYSTEM INITIALIZATION COMPLETE")
    print("="*80 + "\n")


# === BACKGROUND LOOPS ===

async def telemetry_refresh_loop(interval: float = 5.0):
    """Continuously refresh telemetry snapshots for all vehicles"""
    while True:
        try:
            for vehicle_id in list(VEHICLES.keys()):
                snapshot = VehicleDataGenerator.generate_telemetry_stream(vehicle_id)
                SENSOR_DATA[vehicle_id] = snapshot
        except Exception as exc:
            print(f"⚠️ Telemetry refresh error: {exc}")
        await asyncio.sleep(interval)


def _parse_datetime(date_str: str, time_str: str) -> datetime:
    try:
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")
    except Exception:
        return datetime.now()


async def appointment_progress_loop():
    """Advance scheduled appointments through lifecycle and update service records"""
    while True:
        now = datetime.now()
        try:
            for appointment in list(APPOINTMENTS.values()):
                status = appointment.get("status")
                scheduled_dt = _parse_datetime(appointment.get("appointment_date", now.strftime("%Y-%m-%d")), appointment.get("appointment_time", "10:00 AM"))

                if status == "scheduled" and now >= scheduled_dt:
                    appointment["status"] = "in_progress"
                    appointment["work_started_at"] = now.isoformat()
                elif status == "in_progress":
                    started_at = appointment.get("work_started_at")
                    if not started_at:
                        appointment["work_started_at"] = now.isoformat()
                        started_at = appointment["work_started_at"]
                    started_dt = datetime.fromisoformat(started_at)
                    duration_minutes = int(appointment.get("estimated_duration", 60))
                    if now >= started_dt + timedelta(minutes=duration_minutes):
                        appointment["status"] = "completed"
                        appointment["completed_at"] = now.isoformat()
                        _append_service_record_from_appointment(appointment)
        except Exception as exc:
            print(f"⚠️ Appointment lifecycle error: {exc}")

        await asyncio.sleep(10)


def _append_service_record_from_appointment(appointment: Dict):
    """Create a service history entry once an appointment is completed"""
    vehicle_id = appointment.get("vehicle_id")
    if not vehicle_id:
        return

    service_id = appointment.get("history_id")
    if not service_id:
        service_id = f"SRV-{appointment['id']}"
        appointment["history_id"] = service_id

    if service_id in SERVICE_HISTORY:
        return

    SERVICE_HISTORY[service_id] = {
        "id": service_id,
        "vehicle_id": vehicle_id,
        "service_date": appointment.get("appointment_date", datetime.now().strftime("%Y-%m-%d")),
        "service_type": appointment.get("service_type", "General Service"),
        "status": "completed",
        "technician": appointment.get("assigned_technician", "AI-TECH"),
        "cost": round(appointment.get("estimated_cost", 0.0), 2),
        "parts_replaced": appointment.get("parts_replaced", "Reviewed"),
        "remarks": appointment.get("notes", "Service completed via autonomous workflow"),
        "customer_rating": 0
    }


def _ensure_priority_appointment(customer_id: Optional[str], vehicle_id: Optional[str], metadata: Dict[str, Any], priority: str) -> None:
    if not customer_id or not vehicle_id:
        return

    existing = next(
        (a for a in APPOINTMENTS.values() if a.get("vehicle_id") == vehicle_id and a.get("status") in {"scheduled", "in_progress"}),
        None,
    )
    if existing:
        return

    appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
    when = datetime.now() + timedelta(hours=2)
    APPOINTMENTS[appointment_id] = {
        "id": appointment_id,
        "vehicle_id": vehicle_id,
        "customer_id": customer_id,
        "appointment_date": when.strftime("%Y-%m-%d"),
        "appointment_time": when.strftime("%I:%M %p"),
        "service_type": metadata.get("service_type", "AI Recommended Maintenance"),
        "status": "scheduled",
        "priority": priority or "high",
        "service_center": "Main Service Center",
        "estimated_duration": 90,
        "estimated_cost": round(metadata.get("estimated_cost", 250.0), 2),
        "created_at": datetime.now().isoformat(),
        "notes": "Voice agent confirmed appointment",
        "assigned_technician": f"Tech-{uuid.uuid4().hex[:2].upper()}",
    }


def _handle_voice_intent(event: VoiceIntentEvent) -> None:
    prediction_id = event.metadata.get("prediction_id")
    prediction = PREDICTIONS.get(prediction_id) if prediction_id else None

    if prediction:
        if event.intent == "confirm_service":
            prediction["status"] = "appointment_scheduled"
            prediction["voice_confirmed_at"] = datetime.now().isoformat()
            prediction["confirmed_channel"] = "voice"
        elif event.intent == "escalate_human":
            prediction["status"] = "awaiting_human_followup"
        else:
            prediction.setdefault("voice_notes", []).append({
                "intent": event.intent,
                "transcript": event.transcript,
            })

    if event.intent == "confirm_service":
        _ensure_priority_appointment(event.customer_id, event.metadata.get("vehicle_id"), event.metadata, (prediction or {}).get("priority", "high"))

async def prediction_health_monitor(interval: float = 30.0):
    """Adjust vehicle health based on outstanding predictions to keep data consistent"""
    while True:
        try:
            for prediction in PREDICTIONS.values():
                vehicle = VEHICLES.get(prediction.get("vehicle_id"))
                if not vehicle:
                    continue
                priority = prediction.get("priority", "medium").lower()
                if priority == "critical":
                    vehicle["health_status"] = "critical"
                elif priority == "high" and vehicle.get("health_status") not in {"critical"}:
                    vehicle["health_status"] = "needs_attention"
        except Exception as exc:
            print(f"⚠️ Prediction monitor error: {exc}")
        await asyncio.sleep(interval)

# === API ENDPOINTS ===

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "system": "AI Predictive Vehicle Maintenance System",
        "version": "1.0.0",
        "status": "operational",
        "components": {
            "master_agent": "active",
            "worker_agents": len(Master.workers),
            "ueba_security": "enabled",
            "chat_agent": "active"
        },
        "stats": {
            "total_customers": len(CUSTOMERS),
            "total_vehicles": len(VEHICLES),
            "active_predictions": len([p for p in PREDICTIONS.values() if p["status"] in ["pending", "diagnosed"]]),
            "scheduled_appointments": len([a for a in APPOINTMENTS.values() if a["status"] == "scheduled"])
        }
    }

@app.post("/register_customer")
async def register_customer(customer: CustomerModel):
    """Register a new customer and vehicle"""
    CUSTOMERS[customer.id] = customer.dict()
    
    # Create vehicle record if it doesn't exist
    if customer.vehicle_id not in VEHICLES:
        VEHICLES[customer.vehicle_id] = {
            "id": customer.vehicle_id,
            "customer_id": customer.id,
            "model": "Unknown Model",
            "model_number": "TBD",
            "mileage": 0,
            "health_status": "good",
            "last_service_date": None,
            "next_service_due": None
        }
    
    return {
        "message": f"Customer {customer.name} registered successfully",
        "customer_id": customer.id,
        "vehicle_id": customer.vehicle_id
    }

@app.get("/customers")
async def get_customers():
    """Get all customers"""
    return {"customers": list(CUSTOMERS.values()), "total": len(CUSTOMERS)}

@app.get("/customer/{customer_id}")
async def get_customer(customer_id: str):
    """Get specific customer details"""
    customer = CUSTOMERS.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    vehicle_id = customer.get("vehicle_id")
    vehicle = VEHICLES.get(vehicle_id)
    
    return {
        "customer": customer,
        "vehicle": vehicle,
        "sensor_data": SENSOR_DATA.get(vehicle_id),
        "active_predictions": [p for p in PREDICTIONS.values() if p["vehicle_id"] == vehicle_id],
        "appointments": [a for a in APPOINTMENTS.values() if a["customer_id"] == customer_id]
    }

@app.get("/vehicles")
async def get_vehicles():
    """Get all vehicles"""
    return {"vehicles": list(VEHICLES.values()), "total": len(VEHICLES)}

@app.get("/vehicle/{vehicle_id}")
async def get_vehicle(vehicle_id: str):
    """Get specific vehicle details"""
    vehicle = VEHICLES.get(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return {
        "vehicle": vehicle,
        "sensor_data": SENSOR_DATA.get(vehicle_id),
        "predictions": [p for p in PREDICTIONS.values() if p["vehicle_id"] == vehicle_id],
        "service_history": [s for s in SERVICE_HISTORY.values() if s["vehicle_id"] == vehicle_id]
    }

# === API ALIASES EXPECTED BY FRONTEND ===

@app.get("/api/vehicle")
async def api_vehicle_list():
    # return a simple list of vehicles (array) to match frontend expectation
    return list(VEHICLES.values())

@app.get("/api/vehicle/{vehicle_id}")
async def api_vehicle_detail(vehicle_id: str):
    v = VEHICLES.get(vehicle_id)
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return v

@app.get("/api/vehicle/{vehicle_id}/telemetry")
async def api_vehicle_telemetry(vehicle_id: str):
    if vehicle_id not in VEHICLES:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    # produce a fresh snapshot using generator
    snapshot = VehicleDataGenerator.generate_telemetry_stream(vehicle_id)
    SENSOR_DATA[vehicle_id] = snapshot
    return {"status": "online", "last": snapshot}

@app.get("/api/user")
async def api_user_list():
    # return list of customers for simple UI binding
    return list(CUSTOMERS.values())

class ChatAPIPayload(BaseModel):
    user_id: str
    message: str

@app.post("/api/agents/chat")
async def api_agents_chat(payload: ChatAPIPayload):
    if not ChatAgent:
        raise HTTPException(status_code=503, detail="Chat agent not initialized")
    if payload.user_id not in CUSTOMERS:
        raise HTTPException(status_code=404, detail="User not found")
    reply = await ChatAgent.process_message(payload.user_id, payload.message)
    return {"reply": reply}

class SchedulePayload(BaseModel):
    vehicle_id: str
    slot_id: str
    user_id: str

@app.post("/api/service/schedule")
async def api_service_schedule(body: SchedulePayload):
    # Create a simple appointment using provided slot
    if body.vehicle_id not in VEHICLES or body.user_id not in CUSTOMERS:
        raise HTTPException(status_code=404, detail="Vehicle or user not found")
    appointment_id = f"APT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    date_str = body.slot_id.split("T")[0] if "T" in body.slot_id else datetime.now().strftime("%Y-%m-%d")
    time_str = body.slot_id.split("T")[1] if "T" in body.slot_id else "10:00"
    apt = {
        "id": appointment_id,
        "vehicle_id": body.vehicle_id,
        "customer_id": body.user_id,
        "appointment_date": date_str,
        "appointment_time": time_str,
        "service_type": "General Service",
        "status": "scheduled",
        "priority": "medium",
        "service_center": "Main Service Center",
    }
    APPOINTMENTS[appointment_id] = apt
    return {"message": "scheduled", "appointment": apt}

# === WebSocket for Telemetry ===

@app.websocket("/ws/telemetry/{vehicle_id}")
async def ws_telemetry(websocket: WebSocket, vehicle_id: str):
    await websocket.accept()
    try:
        while True:
            if vehicle_id not in VEHICLES:
                await websocket.send_json({"status": "offline", "vehicle_id": vehicle_id})
            else:
                snapshot = VehicleDataGenerator.generate_telemetry_stream(vehicle_id)
                SENSOR_DATA[vehicle_id] = snapshot
                snapshot.update({"status": "online"})
                await websocket.send_json(snapshot)
            await asyncio.sleep(2)
    except Exception:
        # client disconnected or error
        try:
            await websocket.close()
        except Exception:
            pass

# === Minimal JWT auth for UI ===

@app.post("/api/login")
async def api_login(body: LoginModel):
    # very simple: accept any non-empty credentials and mint a token
    if not body.email or not body.password:
        raise HTTPException(status_code=400, detail="Email and password required")
    if HAS_JOSE:
        token = jose_jwt.encode({"sub": body.email, "iat": int(datetime.utcnow().timestamp())}, SECRET_KEY, algorithm=ALGORITHM)
    else:
        token = base64.b64encode(body.email.encode()).decode()
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/me")
async def api_me(token: Optional[str] = None):
    # token can be supplied via query for simplicity in demo
    # real implementation should use Authorization header and OAuth2PasswordBearer
    if not token:
        return {"authenticated": False}
    try:
        if HAS_JOSE:
            payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return {"authenticated": True, "email": payload.get("sub")}
        else:
            email = base64.b64decode(token.encode()).decode()
            return {"authenticated": True, "email": email}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/sensors/{vehicle_id}")
async def get_sensor_data(vehicle_id: str):
    """Get real-time sensor data for a vehicle"""
    if vehicle_id not in VEHICLES:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Generate fresh telemetry data
    sensor_data = VehicleDataGenerator.generate_telemetry_stream(vehicle_id)
    SENSOR_DATA[vehicle_id] = sensor_data
    
    return {"vehicle_id": vehicle_id, "data": sensor_data, "status": "online"}

@app.post("/sensors/update")
async def update_sensor_data(data: TelemetryDataModel):
    """Update sensor data for a vehicle"""
    vehicle_id = data.vehicle_id
    
    if vehicle_id not in VEHICLES:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    sensor_data = data.dict()
    sensor_data["timestamp"] = datetime.now().isoformat()
    SENSOR_DATA[vehicle_id] = sensor_data
    
    return {"message": "Sensor data updated", "vehicle_id": vehicle_id}

@app.get("/predictions")
async def get_predictions():
    """Get all predictions"""
    return {
        "predictions": list(PREDICTIONS.values()),
        "total": len(PREDICTIONS),
        "by_status": {
            "pending": len([p for p in PREDICTIONS.values() if p["status"] == "pending"]),
            "diagnosed": len([p for p in PREDICTIONS.values() if p["status"] == "diagnosed"]),
            "customer_contacted": len([p for p in PREDICTIONS.values() if p["status"] == "customer_contacted"]),
            "appointment_scheduled": len([p for p in PREDICTIONS.values() if p["status"] == "appointment_scheduled"]),
            "voice_confirmed": len([p for p in PREDICTIONS.values() if p["status"] == "voice_confirmed"]),
            "awaiting_human_followup": len([p for p in PREDICTIONS.values() if p["status"] == "awaiting_human_followup"]),
        }
    }

@app.get("/predictions/{vehicle_id}")
async def get_vehicle_predictions(vehicle_id: str):
    """Get predictions for a specific vehicle"""
    predictions = [p for p in PREDICTIONS.values() if p["vehicle_id"] == vehicle_id]
    return {"vehicle_id": vehicle_id, "predictions": predictions, "total": len(predictions)}

@app.get("/appointments")
async def get_appointments():
    """Get all appointments"""
    return {
        "appointments": list(APPOINTMENTS.values()),
        "total": len(APPOINTMENTS),
        "scheduled": len([a for a in APPOINTMENTS.values() if a["status"] == "scheduled"])
    }

@app.post("/appointments/book")
async def book_appointment(appointment: AppointmentModel):
    """Book a service appointment"""
    vehicle = VEHICLES.get(appointment.vehicle_id)
    customer = CUSTOMERS.get(appointment.customer_id)
    
    if not vehicle or not customer:
        raise HTTPException(status_code=404, detail="Vehicle or customer not found")
    
    appointment_id = f"APT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    apt_data = {
        "id": appointment_id,
        "vehicle_id": appointment.vehicle_id,
        "customer_id": appointment.customer_id,
        "appointment_date": appointment.preferred_date or (datetime.now()).strftime("%Y-%m-%d"),
        "appointment_time": "10:00 AM",
        "service_type": appointment.service_type,
        "status": "scheduled",
        "priority": "medium",
        "service_center": "Main Service Center",
        "estimated_duration": 75,
        "created_at": datetime.now().isoformat()
    }
    
    APPOINTMENTS[appointment_id] = apt_data
    
    return {
        "message": "Appointment booked successfully",
        "appointment": apt_data
    }

@app.post("/chat")
async def chat(message: ChatMessageModel):
    """Chat with AI agent"""
    if not ChatAgent:
        raise HTTPException(status_code=503, detail="Chat agent not initialized")
    
    customer = CUSTOMERS.get(message.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    response = await ChatAgent.process_message(message.customer_id, message.message)
    
    return ChatResponseModel(
        customer_id=message.customer_id,
        response=response,
        timestamp=datetime.now().isoformat()
    )

@app.get("/chat/history/{customer_id}")
async def get_chat_history(customer_id: str):
    """Get chat history for a customer"""
    if not ChatAgent:
        raise HTTPException(status_code=503, detail="Chat agent not initialized")
    
    history = ChatAgent.get_conversation_history(customer_id)
    return {"customer_id": customer_id, "history": history, "total_messages": len(history)}

@app.get("/ueba/report")
async def get_ueba_report():
    """Get UEBA security report"""
    report = UEBA.generate_security_report()
    anomalies = UEBA.get_anomaly_report()
    
    return {
        "report": report,
        "total_anomalies": len(anomalies),
        "recent_anomalies": anomalies[-10:],
        "agent_statistics": {
            agent: UEBA.get_agent_statistics(agent) 
            for agent in UEBA.agent_baselines.keys()
        }
    }

@app.post("/ueba/simulate_threat")
async def simulate_threat():
    """Simulate a security threat (for demonstration)"""
    UEBA.simulate_security_threat()
    return {"message": "Security threat simulation completed", "check_logs": "Review UEBA report for details"}

@app.get("/service_history/{vehicle_id}")
async def get_service_history(vehicle_id: str):
    """Get service history for a vehicle"""
    history = [s for s in SERVICE_HISTORY.values() if s["vehicle_id"] == vehicle_id]
    return {"vehicle_id": vehicle_id, "history": history, "total_services": len(history)}

@app.get("/dashboard")
async def get_dashboard():
    """Get dashboard statistics"""
    return {
        "system_overview": {
            "total_customers": len(CUSTOMERS),
            "total_vehicles": len(VEHICLES),
            "total_predictions": len(PREDICTIONS),
            "scheduled_appointments": len([a for a in APPOINTMENTS.values() if a["status"] == "scheduled"])
        },
        "vehicle_health": {
            "excellent": len([v for v in VEHICLES.values() if v["health_status"] == "excellent"]),
            "good": len([v for v in VEHICLES.values() if v["health_status"] == "good"]),
            "needs_attention": len([v for v in VEHICLES.values() if v["health_status"] == "needs_attention"]),
            "critical": len([v for v in VEHICLES.values() if v["health_status"] == "critical"])
        },
        "predictions_by_priority": {
            "critical": len([p for p in PREDICTIONS.values() if p.get("priority") == "critical"]),
            "high": len([p for p in PREDICTIONS.values() if p.get("priority") == "high"]),
            "medium": len([p for p in PREDICTIONS.values() if p.get("priority") == "medium"]),
            "low": len([p for p in PREDICTIONS.values() if p.get("priority") == "low"])
        },
        "master_agent": {
            "status": "running" if Master.loop_running else "stopped",
            "cycle_count": Master.cycle_count,
            "registered_workers": len(Master.workers)
        },
        "ueba_security": {
            "total_logs": len(UEBA.behaviour_log),
            "total_anomalies": len(UEBA.get_anomaly_report()),
            "alert_count": UEBA.alert_count
        }
    }

@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics (alias endpoint)"""
    return await get_dashboard()

# === ADMIN ENDPOINTS ===

@app.post("/admin/models/enable_claude")
async def enable_claude_for_all():
    SETTINGS.llm_provider = "anthropic"
    SETTINGS.llm_model = "claude-3-5-sonnet-20241022"
    SETTINGS.llm_enabled = True
    # Re-init ChatAgent to pick new settings
    global ChatAgent
    ChatAgent = ChatAIAgent(CUSTOMERS, VEHICLES, SENSOR_DATA, PREDICTIONS, APPOINTMENTS, SERVICE_HISTORY)
    return {"message": "Claude Sonnet enabled for all clients", "provider": SETTINGS.llm_provider, "model": SETTINGS.llm_model, "enabled": SETTINGS.llm_enabled}

@app.post("/admin/models/disable_llm")
async def disable_llm():
    SETTINGS.llm_enabled = False
    global ChatAgent
    ChatAgent = ChatAIAgent(CUSTOMERS, VEHICLES, SENSOR_DATA, PREDICTIONS, APPOINTMENTS, SERVICE_HISTORY)
    return {"message": "LLM disabled for all clients", "enabled": SETTINGS.llm_enabled}

@app.get("/admin/models/status")
async def llm_status():
    return {"provider": SETTINGS.llm_provider, "model": SETTINGS.llm_model, "enabled": SETTINGS.llm_enabled}

# === STARTUP AND BACKGROUND TASKS ===

@app.on_event("startup")
async def startup_event():
    """Initialize system and start Master Agent on startup"""
    initialize_system()
    
    # Start Master Agent orchestration in background
    global _orchestration_task, _telemetry_task, _appointment_task, _prediction_task

    _orchestration_task = asyncio.create_task(Master.orchestrate())
    _telemetry_task = asyncio.create_task(telemetry_refresh_loop())
    _appointment_task = asyncio.create_task(appointment_progress_loop())
    _prediction_task = asyncio.create_task(prediction_health_monitor())
    
    print("🚀 Server started and Master Agent orchestration initiated")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    Master.stop()
    for task in [_orchestration_task, _telemetry_task, _appointment_task, _prediction_task]:
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    print("\n👋 System shutdown complete")

# === MAIN ENTRY POINT ===

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚗 AI PREDICTIVE VEHICLE MAINTENANCE SYSTEM")
    print("="*80)
    print("\nStarting server...")
    print("API Documentation: http://localhost:8000/docs")
    print("="*80 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
