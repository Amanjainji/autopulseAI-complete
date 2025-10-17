# AI Predictive Vehicle Maintenance System

## 🚗 Overview

A comprehensive Agentic AI solution for predictive vehicle maintenance that autonomously monitors vehicle health, predicts failures, and proactively engages customers. The system features a Master Agent orchestrating multiple Worker AI agents with UEBA (User and Entity Behavior Analytics) security monitoring.

## 🎯 Key Features

### Master-Worker Agent Architecture
- **Master Agent**: Main orchestrator coordinating all worker agents and managing workflow
- **Data Analysis Agent**: Analyzes streaming vehicle telematics and sensor data
- **Diagnosis Agent**: Runs predictive models for component failures
- **Customer Engagement Agent**: Initiates personalized customer conversations
- **Scheduling Agent**: Manages appointment scheduling based on priority
- **Feedback Agent**: Collects post-service customer satisfaction
- **Manufacturing Insights Agent**: RCA/CAPA analysis for quality improvement

### UEBA Security Layer
- Behavioral baseline monitoring for each AI agent
- Anomaly detection for unauthorized resource access
- Real-time alerts for suspicious agent behavior
- Complete audit trail of all agent activities
- Example: Detects if Scheduling Agent tries to access sensor data

### Customer Experience
- **AI Chat Agent**: 24/7 conversational interface for customers
- **Voice Command Center**: Human-like outbound & inbound calls via Twilio (with offline TTS fallback)
- **Mobile app notifications**: Appointment reminders and alerts
- **Personalized recommendations**: Context-aware maintenance suggestions

### Predictive Maintenance
- Real-time vehicle telematics monitoring
- Early warning detection from sensor patterns
- Failure probability calculation
- Proactive service scheduling
- Service demand forecasting

### Manufacturing Feedback Loop
- Recurring defect pattern analysis
- Root Cause Analysis (RCA) automation
- Corrective and Preventive Actions (CAPA)
- Quality insights fed back to manufacturing
- Design improvement recommendations

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        MASTER AGENT                          │
│              (Main Orchestrator + UEBA Monitor)              │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │  Data   │    │Diagnosis│    │Customer │
    │Analysis │    │  Agent  │    │Engage   │
    └─────────┘    └─────────┘    └─────────┘
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │Schedule │    │Feedback │    │Manufact │
    │  Agent  │    │  Agent  │    │Insights │
    └─────────┘    └─────────┘    └─────────┘
         │               │               │
    ┌────▼───────────────▼───────────────▼────┐
    │            Data Layer                     │
    │  Customers | Vehicles | Sensors | etc.   │
    └───────────────────────────────────────────┘
```

## 📁 Project Structure

```
ey-th/
├── main_app.py              # Main FastAPI application
├── agents.py                # All Worker AI Agents
├── ueba_security.py         # UEBA Security Monitor
├── chat_agent.py            # Customer Chat AI Agent
├── voice_agent.py           # Voice outreach orchestration (Twilio/offline)
├── data_generator.py        # Synthetic data generator
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── vehicle_maintenance.db  # SQLite database (auto-created)
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 2: Run the Application

```powershell
python main_app.py
```

The server will start on `http://localhost:8000`

### Step 3: Access API Documentation

Open your browser and navigate to:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## � Voice Agent Integration

The voice assistant can operate in two modes:

### Option A — Twilio Programmable Voice (recommended)

1. Provision a Twilio phone number capable of voice calls.
2. Set the following environment variables before starting the backend:

   ```powershell
   setx TWILIO_ACCOUNT_SID "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   setx TWILIO_AUTH_TOKEN "your_auth_token"
   setx TWILIO_CALLER_ID "+15551234567"
   setx VOICE_WEBHOOK_BASE_URL "https://your-public-domain"
   ```

3. Expose the FastAPI server publicly (e.g., via [ngrok](https://ngrok.com/)) so Twilio can reach `/api/voice/twiml/{call_id}` and `/api/voice/status`.
4. Outbound calls will automatically use the Amazon Polly "Joanna" voice for a natural delivery. Customers can confirm (press 1) or request a human follow-up (press 2).

### Option B — Offline Demo (pyttsx3)

If Twilio credentials are not provided, the system falls back to locally synthesised call scripts:

- Install optional dependency `pyttsx3` (already listed in `requirements.txt`).
- Generated audio files are stored under the `voice_calls/` directory.
- Each script is logged with timestamps so you can review the simulated conversation flow.

### Monitoring Voice Activity

- `GET /api/voice/events` — view recent call attempts, intents, and status changes.
- `POST /api/voice/outbound` — trigger a manual test call with custom messaging.

The customer engagement agent automatically triggers outbound calls for **high** and **critical** predictions.

## �📊 Synthetic Data

The system automatically generates data for **10 sample vehicles** including:
- Customer information (name, contact, purchase date)
- Vehicle details (model, VIN, mileage, warranty)
- Real-time sensor data (engine temp, oil pressure, battery, tires)
- Service history (past maintenance records)
- Diagnostic trouble codes (DTCs)

### Sample Vehicle Models:
1. Tesla Model S
2. BMW X5
3. Toyota Camry
4. Ford F-150
5. Honda Accord
6. Mercedes-Benz C-Class
7. Audi Q7
8. Chevrolet Silverado
9. Nissan Altima
10. Hyundai Tucson

## 🔌 API Endpoints

### Core Endpoints

#### System Status
```
GET /
```
Returns system overview, component status, and statistics.

#### Customer Management
```
POST /register_customer
GET /customers
GET /customer/{customer_id}
```

#### Vehicle Management
```
GET /vehicles
GET /vehicle/{vehicle_id}
GET /sensors/{vehicle_id}
POST /sensors/update
```

#### Predictions & Diagnostics
```
GET /predictions
GET /predictions/{vehicle_id}
```

#### Appointments
```
GET /appointments
POST /appointments/book
```

#### Chat Interface
```
POST /chat
GET /chat/history/{customer_id}
```

#### Voice Engagement
```
POST /api/voice/outbound
POST /api/voice/status
POST /api/voice/gather/{call_id}
GET  /api/voice/events
```
> Twilio automatically calls `/api/voice/twiml/{call_id}` during live calls; you typically won't invoke it manually.

#### UEBA Security
```
GET /ueba/report
POST /ueba/simulate_threat
```

#### Dashboard
```
GET /dashboard
```

## 💬 Chat AI Agent Examples

### Customer Interactions

**Check Vehicle Status:**
```
Customer: "How is my car doing?"
AI: Provides comprehensive health report with sensor data, predictions, and recommendations
```

**Book Service:**
```
Customer: "I need to schedule service"
AI: Shows predicted issues, recommends services, offers available time slots
```

**Report Problem:**
```
Customer: "My car is making a strange noise"
AI: Identifies potential causes, recommends urgent inspection, offers to book appointment
```

**Service History:**
```
Customer: "Show my service history"
AI: Displays past services, costs, ratings, and maintenance patterns
```

## 🔐 UEBA Security Monitoring

### What is UEBA?

UEBA (User and Entity Behavior Analytics) uses machine learning to establish behavioral baselines for AI agents and detect anomalies indicating potential security threats.

### Security Features

1. **Baseline Monitoring**: Each agent has defined allowed resources
2. **Anomaly Detection**: Flags unauthorized access attempts
3. **Activity Logging**: Complete audit trail in database
4. **Real-time Alerts**: Immediate notification of suspicious behavior
5. **Automated Response**: Blocks anomalous activities

### Example Security Alert

```
⚠️ UEBA SECURITY ALERT
Agent: SchedulingAgent
Action: Attempting unauthorized access to telematics data
Resource: sensor_data
Anomaly Score: 0.95 (Threshold: 0.7)
ACTION TAKEN: Activity blocked and logged
```

## 🔧 Agent Workflow

### Orchestration Cycle (Every 20 seconds)

1. **Data Analysis Agent**
   - Scans all vehicle sensor data
   - Identifies anomalies and early warning signs
   - Creates predictions for maintenance needs
   - Priority: Overheating, low oil, battery issues, tire pressure, error codes

2. **Diagnosis Agent**
   - Analyzes predictions from Data Analysis
   - Calculates failure probability
   - Assigns priority levels (Critical, High, Medium, Low)
   - Updates prediction status

3. **Customer Engagement Agent**
   - Contacts customers with diagnosed issues
   - Generates persuasive, personalized messages
   - Explains vehicle condition and urgency
   - Recommends service booking

4. **Scheduling Agent**
   - Processes customer responses (simulated 85% acceptance)
   - Finds available appointment slots
   - Books appointments based on priority
   - Manages service center capacity

5. **Feedback Agent**
   - Collects post-service customer ratings
   - Updates vehicle health status
   - Records satisfaction metrics

6. **Manufacturing Insights Agent**
   - Identifies recurring defect patterns
   - Performs RCA (Root Cause Analysis)
   - Suggests CAPA (Corrective and Preventive Actions)
   - Feeds insights to manufacturing team

> Background tasks continuously refresh live telemetry feeds, auto-progress service appointments, and align vehicle health states with outstanding predictions to keep each agent operating with up-to-date context.

## 📈 Edge Cases Handled

1. **Declined Appointments**: System follows up with customers who decline
2. **Urgent Failure Alerts**: Critical issues get priority scheduling (2-3 days)
3. **Multi-Vehicle Fleet**: Can manage multiple vehicles per customer
4. **Recurring Defects**: Identifies patterns across vehicle models
5. **Service Center Capacity**: Manages appointment availability
6. **Sensor Data Offline**: Handles missing telemetry gracefully
7. **Security Threats**: UEBA detects and blocks anomalous agent behavior

## 🏭 Manufacturing Feedback Loop

### RCA/CAPA Analysis

When the system detects **recurring defects** (2+ occurrences of same issue in same model):

1. **Root Cause Identification**
   - Example: "Inadequate cooling system capacity"

2. **Corrective Action**
   - Example: "Upgrade cooling system for affected vehicles"

3. **Preventive Action**
   - Example: "Redesign cooling system with 20% higher capacity"

4. **Manufacturing Team Notification**
   - Automated reports with defect patterns
   - Design improvement recommendations
   - Supplier quality issues flagged

## 🎨 Demonstration Scenarios

### Scenario 1: Normal Maintenance Cycle
```
1. Vehicle VEH003 shows high mileage (48,000 miles)
2. Data Analysis Agent flags for inspection
3. Diagnosis Agent confirms medium priority
4. Customer Engagement Agent contacts owner
5. Scheduling Agent books appointment
6. Service completed → Feedback collected
```

### Scenario 2: Critical Failure Prediction
```
1. Vehicle VEH005 sensor shows engine overheating (108°F)
2. Data Analysis Agent creates critical prediction
3. Diagnosis Agent assigns failure probability 85%
4. Customer Engagement Agent sends urgent message
5. Scheduling Agent books within 2 days
6. Manufacturing Insights flags recurring cooling issue
7. CAPA report sent to manufacturing team
```

### Scenario 3: Security Threat Detection
```
1. Scheduling Agent attempts to access sensor_data
2. UEBA detects unauthorized resource access
3. Anomaly score: 0.95 (above 0.7 threshold)
4. Activity blocked immediately
5. Alert logged and sent to security team
6. Audit trail recorded in database
```

## 📱 Customer Interaction Channels

### Primary: Voice-Based Virtual Agent
- Natural language understanding
- Persuasive conversation flow
- Explains technical issues in simple terms
- Convinces customers to book service

### Secondary: Mobile App
- Push notifications for predictions
- Appointment reminders (24 hours before)
- Service completion updates
- Real-time vehicle health dashboard

### Tertiary: Chat Interface
- 24/7 AI-powered support
- Context-aware responses
- Multi-turn conversations
- Booking and inquiry handling

## 🔍 Testing the System

### 1. Check System Status
```bash
curl http://localhost:8000/
```

### 2. View All Vehicles
```bash
curl http://localhost:8000/vehicles
```

### 3. Get Predictions
```bash
curl http://localhost:8000/predictions
```

### 4. Chat with AI Agent
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"CUST001","message":"How is my car doing?"}'
```

### 5. View UEBA Security Report
```bash
curl http://localhost:8000/ueba/report
```

### 6. Simulate Security Threat
```bash
curl -X POST http://localhost:8000/ueba/simulate_threat
```

### 7. View Dashboard
```bash
curl http://localhost:8000/dashboard
```

### 8. Trigger a Voice Outreach Test
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/voice/outbound -Body (@{
   customer_id = "CUST001"
   customer_name = "Customer 1"
   phone = "+15551234567"
   message = "We detected elevated engine temperature and recommend a diagnostic service this week."
} | ConvertTo-Json) -ContentType "application/json"
```
> Replace the phone number with a verified Twilio recipient when using live calls.

## 📊 Database Schema

The system uses SQLite with the following tables:
- `customers` - Customer information
- `vehicles` - Vehicle details and health status
- `sensor_data` - Real-time telemetry data
- `service_records` - Maintenance history
- `appointments` - Scheduled service appointments
- `predictions` - AI-generated maintenance predictions
- `manufacturing_feedback` - RCA/CAPA insights
- `agent_activity_log` - UEBA security audit trail

## 🎯 Key Metrics

The system tracks:
- Vehicle health distribution (Excellent/Good/Needs Attention/Critical)
- Prediction accuracy and confidence scores
- Customer acceptance rate (target: 80%+)
- Appointment scheduling efficiency
- Agent activity and anomaly rates
- Service center capacity utilization
- Customer satisfaction scores

## 🚀 Future Enhancements

1. **ML Model Integration**: Replace rule-based predictions with trained models
2. **Real Telematics API**: Connect to actual vehicle telematics systems
3. **Multi-Tenant Support**: Handle multiple service centers
4. **Advanced NLP**: Improve chat agent with transformer models
5. **Fleet Management**: Bulk operations for commercial fleets
6. **Blockchain Audit**: Immutable audit trail for UEBA logs
7. **Predictive Parts Inventory**: Forecast parts demand
8. **Integration with OEM Systems**: Direct manufacturing feedback

## 📞 Support

For questions or issues:
- Check API documentation: http://localhost:8000/docs
- Review UEBA logs: `GET /ueba/report`
- Inspect database: `vehicle_maintenance.db`

## 📜 License

This is a demonstration system for educational and proof-of-concept purposes.

---

**Built with ❤️ using FastAPI, Python, and AI Agent Architecture**
