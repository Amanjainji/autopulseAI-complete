from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random, asyncio
import sqlite3
import json
from enum import Enum

app = FastAPI(title="AI Vehicle Maintenance Backend")

# === DATABASE INITIALIZATION ===
def init_database():
    conn = sqlite3.connect('vehicle_maintenance.db')
    cursor = conn.cursor()
    
    # Customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT,
            purchase_date TEXT NOT NULL,
            vehicle_id TEXT NOT NULL
        )
    ''')
    
    # Vehicles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id TEXT PRIMARY KEY,
            customer_id TEXT,
            model TEXT NOT NULL,
            model_number TEXT NOT NULL,
            vin TEXT,
            registration_number TEXT,
            manufacturing_date TEXT,
            purchase_date TEXT,
            warranty_expiry TEXT,
            mileage INTEGER DEFAULT 0,
            health_status TEXT DEFAULT 'OK',
            last_service_date TEXT,
            next_service_due TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    # Service records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_records (
            id TEXT PRIMARY KEY,
            vehicle_id TEXT NOT NULL,
            service_date TEXT NOT NULL,
            service_type TEXT NOT NULL,
            status TEXT NOT NULL,
            technician TEXT,
            cost REAL,
            parts_replaced TEXT,
            remarks TEXT,
            customer_rating INTEGER,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
        )
    ''')
    
    # Sensor data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            engine_temp REAL,
            oil_pressure REAL,
            battery_voltage REAL,
            tire_pressure TEXT,
            fuel_level REAL,
            speed REAL,
            rpm REAL,
            error_codes TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
        )
    ''')
    
    # Appointments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id TEXT PRIMARY KEY,
            vehicle_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            service_type TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT,
            estimated_duration INTEGER,
            service_center TEXT,
            notes TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id),
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    # Predictions and diagnostics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id TEXT PRIMARY KEY,
            vehicle_id TEXT NOT NULL,
            prediction_date TEXT NOT NULL,
            predicted_issue TEXT NOT NULL,
            confidence_score REAL,
            priority TEXT,
            estimated_failure_date TEXT,
            recommended_action TEXT,
            parts_at_risk TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
        )
    ''')
    
    # Manufacturing feedback (RCA/CAPA) table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS manufacturing_feedback (
            id TEXT PRIMARY KEY,
            vehicle_model TEXT NOT NULL,
            defect_pattern TEXT NOT NULL,
            occurrence_count INTEGER,
            severity TEXT,
            root_cause TEXT,
            corrective_action TEXT,
            preventive_action TEXT,
            status TEXT,
            created_date TEXT,
            resolved_date TEXT
        )
    ''')
    
    # Agent activity log for UEBA
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            resource_accessed TEXT,
            is_anomalous INTEGER DEFAULT 0,
            anomaly_score REAL
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# === IN-MEMORY CACHE FOR QUICK ACCESS ===
CUSTOMERS = {}
VEHICLES = {}
SERVICE_HISTORY = {}
REALTIME_SENSOR_DATA = {}
PREDICTIONS = {}
APPOINTMENTS = {}

# === ENUMS ===
class ServiceStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HealthStatus(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_ATTENTION = "needs_attention"
    CRITICAL = "critical"

# === MODELS ===
class Customer(BaseModel):
    id: str
    name: str
    phone: str
    email: str
    address: Optional[str] = ""
    purchase_date: str
    vehicle_id: str

class Vehicle(BaseModel):
    id: str
    customer_id: Optional[str] = ""
    model: str
    model_number: str
    vin: Optional[str] = ""
    registration_number: Optional[str] = ""
    manufacturing_date: Optional[str] = ""
    purchase_date: Optional[str] = ""
    warranty_expiry: Optional[str] = ""
    mileage: int = 0
    health_status: str = "good"
    last_service_date: Optional[str] = None
    next_service_due: Optional[str] = None

class ServiceRecord(BaseModel):
    id: str
    vehicle_id: str
    service_date: str
    service_type: str
    status: str
    technician: Optional[str] = ""
    cost: Optional[float] = 0.0
    parts_replaced: Optional[str] = ""
    remarks: Optional[str] = ""
    customer_rating: Optional[int] = 0

class SensorData(BaseModel):
    vehicle_id: str
    timestamp: str
    engine_temp: float
    oil_pressure: float
    battery_voltage: float
    tire_pressure: Dict[str, float]
    fuel_level: float
    speed: float
    rpm: float
    error_codes: List[str] = []

class Appointment(BaseModel):
    id: str
    vehicle_id: str
    customer_id: str
    appointment_date: str
    appointment_time: str
    service_type: str
    status: str
    priority: str = "medium"
    estimated_duration: int = 60
    service_center: str = "Main Service Center"
    notes: Optional[str] = ""

class Prediction(BaseModel):
    id: str
    vehicle_id: str
    prediction_date: str
    predicted_issue: str
    confidence_score: float
    priority: str
    estimated_failure_date: str
    recommended_action: str
    parts_at_risk: str
    status: str = "pending"

class ManufacturingFeedback(BaseModel):
    id: str
    vehicle_model: str
    defect_pattern: str
    occurrence_count: int
    severity: str
    root_cause: str
    corrective_action: str
    preventive_action: str
    status: str
    created_date: str
    resolved_date: Optional[str] = None

class ChatMessage(BaseModel):
    customer_id: str
    message: str
    timestamp: Optional[str] = None

class VoiceInteraction(BaseModel):
    customer_id: str
    transcript: str
    intent: str
    entities: Dict = {}

# === SYNTHETIC VEHICLE DATA GENERATOR ===
class VehicleDataGenerator:
    """Generates synthetic data for 10 example vehicles"""
    
    @staticmethod
    def generate_sample_vehicles():
        vehicles_data = []
        models = [
            ("Tesla Model S", "TMS-2025", "Premium Electric Sedan"),
            ("BMW X5", "BMX5-2024", "Luxury SUV"),
            ("Toyota Camry", "TC-2023", "Reliable Sedan"),
            ("Ford F-150", "FF150-2024", "Heavy Duty Pickup"),
            ("Honda Accord", "HA-2023", "Mid-Size Sedan"),
            ("Mercedes-Benz C-Class", "MBC-2025", "Luxury Sedan"),
            ("Audi Q7", "AQ7-2024", "Premium SUV"),
            ("Chevrolet Silverado", "CS-2023", "Work Truck"),
            ("Nissan Altima", "NA-2024", "Family Sedan"),
            ("Hyundai Tucson", "HT-2025", "Compact SUV")
        ]
        
        for i, (model, model_num, desc) in enumerate(models, 1):
            vehicle_id = f"VEH{i:03d}"
            customer_id = f"CUST-{i:03d}"
            
            # Create customer
            customer = {
                "id": customer_id,
                "name": f"Customer {i}",
                "phone": f"+1-555-{1000+i}",
                "email": f"customer{i}@example.com",
                "address": f"{i}00 Main Street, City {i}",
                "purchase_date": (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d"),
                "vehicle_id": vehicle_id
            }
            
            # Create vehicle
            purchase_date = datetime.strptime(customer["purchase_date"], "%Y-%m-%d")
            last_service = purchase_date + timedelta(days=random.randint(90, 180))
            
            vehicle = {
                "id": vehicle_id,
                "customer_id": customer_id,
                "model": model,
                "model_number": model_num,
                "vin": f"1HGBH41JXMN{109000+i}",
                "registration_number": f"ABC{i:04d}",
                "manufacturing_date": (purchase_date - timedelta(days=30)).strftime("%Y-%m-%d"),
                "purchase_date": customer["purchase_date"],
                "warranty_expiry": (purchase_date + timedelta(days=1095)).strftime("%Y-%m-%d"),
                "mileage": random.randint(5000, 50000),
                "health_status": random.choice(["excellent", "good", "needs_attention"]),
                "last_service_date": last_service.strftime("%Y-%m-%d"),
                "next_service_due": (last_service + timedelta(days=180)).strftime("%Y-%m-%d")
            }
            
            # Generate sensor data
            sensor_data = {
                "vehicle_id": vehicle_id,
                "timestamp": datetime.now().isoformat(),
                "engine_temp": round(random.uniform(85.0, 105.0), 2),
                "oil_pressure": round(random.uniform(25.0, 65.0), 2),
                "battery_voltage": round(random.uniform(12.0, 14.5), 2),
                "tire_pressure": {
                    "front_left": round(random.uniform(30.0, 35.0), 1),
                    "front_right": round(random.uniform(30.0, 35.0), 1),
                    "rear_left": round(random.uniform(30.0, 35.0), 1),
                    "rear_right": round(random.uniform(30.0, 35.0), 1)
                },
                "fuel_level": round(random.uniform(10.0, 95.0), 1),
                "speed": round(random.uniform(0.0, 75.0), 1),
                "rpm": round(random.uniform(800.0, 3500.0), 0),
                "error_codes": [] if random.random() > 0.3 else [f"P{random.randint(100, 999)}"]
            }
            
            # Generate service history
            service_history = []
            for j in range(random.randint(1, 5)):
                service_date = last_service - timedelta(days=j*180)
                service_history.append({
                    "id": f"SRV{i:03d}{j:02d}",
                    "vehicle_id": vehicle_id,
                    "service_date": service_date.strftime("%Y-%m-%d"),
                    "service_type": random.choice(["Oil Change", "Tire Rotation", "Brake Inspection", "Engine Diagnostic"]),
                    "status": "completed",
                    "technician": f"Tech-{random.randint(1, 10)}",
                    "cost": round(random.uniform(50.0, 500.0), 2),
                    "parts_replaced": random.choice(["Oil Filter", "Air Filter", "Brake Pads", "None"]),
                    "remarks": "Service completed successfully",
                    "customer_rating": random.randint(4, 5)
                })
            
            vehicles_data.append({
                "customer": customer,
                "vehicle": vehicle,
                "sensor_data": sensor_data,
                "service_history": service_history
            })
        
        return vehicles_data

# === UEBA - Security Layer ===
class UEBAMonitor:
    """User and Entity Behavior Analytics for AI Agent Security"""
    
    def __init__(self):
        self.behaviour_log = []
        self.agent_baselines = {
            "DataAnalysisAgent": {"allowed_resources": ["sensor_data", "vehicles", "predictions"]},
            "DiagnosisAgent": {"allowed_resources": ["predictions", "vehicles", "sensor_data"]},
            "CustomerEngagementAgent": {"allowed_resources": ["customers", "vehicles", "predictions", "appointments"]},
            "SchedulingAgent": {"allowed_resources": ["appointments", "vehicles", "customers"]},
            "FeedbackAgent": {"allowed_resources": ["service_records", "customers"]},
            "ManufacturingInsightsAgent": {"allowed_resources": ["predictions", "service_records", "manufacturing_feedback"]},
            "MasterAgent": {"allowed_resources": ["all"]}
        }
        self.anomaly_threshold = 0.7
    
    def log_activity(self, agent_name: str, action: str, resource: str = ""):
        """Log agent activity and check for anomalies"""
        timestamp = datetime.now().isoformat()
        anomaly_score = self._calculate_anomaly_score(agent_name, resource)
        is_anomalous = anomaly_score > self.anomaly_threshold
        
        entry = {
            "agent": agent_name,
            "action": action,
            "resource": resource,
            "timestamp": timestamp,
            "is_anomalous": is_anomalous,
            "anomaly_score": anomaly_score
        }
        
        self.behaviour_log.append(entry)
        
        # Store in database
        conn = sqlite3.connect('vehicle_maintenance.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO agent_activity_log (agent_name, action, timestamp, resource_accessed, is_anomalous, anomaly_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (agent_name, action, timestamp, resource, int(is_anomalous), anomaly_score))
        conn.commit()
        conn.close()
        
        if is_anomalous:
            alert_msg = f"⚠️ [UEBA ALERT] Anomalous behavior detected!\n" \
                       f"   Agent: {agent_name}\n" \
                       f"   Action: {action}\n" \
                       f"   Resource: {resource}\n" \
                       f"   Anomaly Score: {anomaly_score:.2f}\n" \
                       f"   Time: {timestamp}"
            print(alert_msg)
            # In production, this would trigger alerts to security team
        
        return not is_anomalous
    
    def _calculate_anomaly_score(self, agent_name: str, resource: str) -> float:
        """Calculate anomaly score based on agent behavior baseline"""
        if agent_name not in self.agent_baselines:
            return 0.9  # Unknown agent = high anomaly score
        
        allowed_resources = self.agent_baselines[agent_name]["allowed_resources"]
        
        if "all" in allowed_resources:
            return 0.0  # Master agent can access everything
        
        if resource and resource not in allowed_resources:
            return 0.95  # Unauthorized resource access
        
        # Check for unusual activity patterns
        recent_actions = [log for log in self.behaviour_log[-20:] if log["agent"] == agent_name]
        if len(recent_actions) > 15:  # Too many actions in short time
            return 0.75
        
        return random.uniform(0.0, 0.3)  # Normal behavior
    
    def get_anomaly_report(self) -> List[Dict]:
        """Get all anomalous activities"""
        return [log for log in self.behaviour_log if log["is_anomalous"]]

UEBA = UEBAMonitor()

# === AGENT ARCHITECTURE ===
class MasterAgent:
    def __init__(self):
        self.workers = {}
        self.loop_running = False

    def register_worker(self, name, worker):
        self.workers[name] = worker
        UEBA.log("MasterAgent", f"Registered {name}")

    async def orchestrate(self):
        while True:
            for name, worker in self.workers.items():
                UEBA.log("MasterAgent", f"Triggering {name}")
                await worker.run()
            await asyncio.sleep(5)

Master = MasterAgent()

class DataAnalysisAgent:
    async def run(self):
        for v_id, v in VEHICLES.items():
            if random.random() < 0.2:
                v.health_status = "Needs Check"
                print(f"[DataAnalysisAgent] Vehicle {v.model} flagged for inspection.")

class DiagnosisAgent:
    async def run(self):
        for v_id, v in VEHICLES.items():
            if v.health_status == "Needs Check":
                print(f"[DiagnosisAgent] Predicting issue for {v.model} ... Possible engine maintenance required.")

class CustomerEngagementAgent:
    async def run(self):
        for c_id, c in CUSTOMERS.items():
            v = VEHICLES.get(c.vehicle_id)
            if v and v.health_status == "Needs Check":
                print(f"[CustomerEngagementAgent] Sending message to {c.name}: ‘Your {v.model} needs service.’")

class SchedulingAgent:
    async def run(self):
        for v_id, v in VEHICLES.items():
            if v.health_status == "Needs Check":
                slot = f"{datetime.now().date()} - 10:30 AM"
                print(f"[SchedulingAgent] Booking slot for {v.model} on {slot}")

# === REGISTER WORKERS ===
Master.register_worker("DataAnalysis", DataAnalysisAgent())
Master.register_worker("Diagnosis", DiagnosisAgent())
Master.register_worker("Engagement", CustomerEngagementAgent())
Master.register_worker("Scheduling", SchedulingAgent())

# === BACKEND ROUTES ===
@app.post("/register_customer")
def register_customer(c: Customer):
    CUSTOMERS[c.id] = c
    VEHICLES[c.vehicle_id] = Vehicle(id=c.vehicle_id, model="Tesla Model S", model_number="TS-2025")
    return {"message": f"Customer {c.name} registered successfully"}

@app.get("/get_vehicle/{vehicle_id}")
def get_vehicle(vehicle_id: str):
    vehicle = VEHICLES.get(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@app.get("/get_sensors/{vehicle_id}")
def get_sensor_data(vehicle_id: str):
    # Mock telematics
    if random.random() < 0.1:
        return {"status": "offline", "data": None}
    else:
        data = {"speed": random.randint(40, 120), "temp": random.randint(70, 110), "oil": random.randint(50, 100)}
        REALTIME_SENSOR_DATA[vehicle_id] = data
        return {"status": "online", "data": data}

@app.on_event("startup")
async def start_agents():
    asyncio.create_task(Master.orchestrate())
