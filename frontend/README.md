# AutoPulse AI - Frontend

A professional, corporate-grade automotive AI dashboard built with **React + Vite**, **TailwindCSS**, **Framer Motion**, **Recharts**, and **Three.js**.

## 🎯 System Architecture

This frontend connects to an **Agentic AI Predictive Maintenance System** with:

### Master Agent (Main Orchestrator)
- Monitors vehicle health data streams and conversational flow
- Coordinates Worker Agents for diagnosis, customer outreach, scheduling, and feedback
- Ensures UEBA-based security compliance
- Initiates and ends customer interactions

### Worker Agents
1. **Data Analysis Agent**: Analyzes streaming telematics + maintenance history to detect early warnings
2. **Diagnosis Agent**: Runs predictive models for component failures and assigns priority
3. **Customer Engagement Agent**: Initiates personalized chatbot conversations to explain issues
4. **Scheduling Agent**: Manages service center capacity and appointment booking
5. **Feedback Agent**: Captures post-service satisfaction and updates records
6. **Manufacturing Quality Insights Module**: Generates RCA/CAPA insights for manufacturing team

### UEBA Security Layer
- Monitors AI agent behavior for anomalies
- Detects unauthorized access attempts (e.g., Scheduling Agent accessing telemetry data)
- Triggers alerts and blocks suspicious actions

## 🎨 Features

### Customer Interface
- **Animated Loader**: Professional brand text animation
- **Dashboard**: 
  - 3D car visualization (Three.js)
  - Real-time telemetry via WebSocket
  - Donut and Line charts (Recharts)
  - AI predictions and notifications
  - Quick actions panel
- **Profile Page**:
  - User details with avatar
  - Vehicle information (model, VIN, warranty, mileage)
  - AI-generated maintenance predictions with priority levels
  - Complete service history with ratings
  - Quick action cards
- **Service Booking**: Date/time selection with capacity-aware scheduling
- **Floating Chat Widget**: Wired to backend AI agent for persuasive, human-like conversations

### Admin/Agent Interface
- **LLM Control Panel**: Enable/disable Claude Sonnet 4.5 globally
- **System Overview**: Real-time metrics (customers, vehicles, predictions, appointments)
- **UEBA Monitoring**: (Ready to expand with anomaly alerts)
- **Agent Activity Monitor**: (Ready to expand with Master/Worker status)

## 🚀 Getting Started

### Installation
```bash
npm install
```

### Development
```bash
npm run dev
```
Frontend runs on: http://localhost:5173

### Production Build
```bash
npm run build
npm run preview
```

## ⚙️ Configuration

### Backend Connection
Edit `src/lib/api.js`:
```javascript
const api = axios.create({ baseURL: "http://localhost:8000" });
```

### WebSocket Telemetry
Connects to: `ws://localhost:8000/ws/telemetry/{vehicleId}`

### JWT Authentication
Token stored in `localStorage` and sent via Authorization header.

## 📁 Project Structure

```
src/
├── components/
│   ├── Loader.jsx              # Animated brand loader
│   ├── Navbar.jsx              # Top navigation with avatar
│   ├── Sidebar.jsx             # Left navigation icons
│   ├── AvatarBtn.jsx           # User avatar button
│   ├── VehicleCard.jsx         # Vehicle display card
│   ├── Car3D.jsx               # Three.js 3D car visualization
│   ├── HealthGraph.jsx         # Recharts line chart
│   ├── DonutChart.jsx          # Recharts donut chart
│   ├── NotificationPanel.jsx   # Alerts panel
│   ├── ChatWidget.jsx          # Floating AI chat
│   └── FooterNav.jsx           # Mobile bottom navigation
├── pages/
│   ├── Login.jsx               # Authentication
│   ├── Signup.jsx              # User registration
│   ├── Dashboard.jsx           # Main customer dashboard
│   ├── Profile.jsx             # User/vehicle profile with AI predictions
│   ├── ServiceBooking.jsx      # Appointment scheduling
│   └── admin/
│       └── AdminPanel.jsx      # LLM control + system metrics
├── lib/
│   ├── api.js                  # Axios instance with JWT interceptor
│   └── useTelemetry.js         # WebSocket hook for live data
├── App.jsx                     # Route configuration
├── main.jsx                    # Entry point
└── styles.css                  # TailwindCSS + custom theme

```

## 🎨 Design System

### Theme
- **Primary Background**: `#0d0f12` (Graphite)
- **Cards**: `rgba(255,255,255,0.04)` (Subtle glass)
- **Accent**: `#00b4ff` (Electric Blue)
- **Text**: White with opacity variants

### Typography
- **Font**: Inter (Google Fonts)
- **Sizes**: Hierarchical scale from xs to 5xl

### Components
- **Cards**: `.card` - Glassmorphism with subtle borders
- **Buttons**: `.btn-primary`, `.btn-ghost`
- **Inputs**: `.input` - Consistent styling with focus states

## 🔌 Backend Integration

### Required Endpoints
- `GET /api/vehicle` - List all vehicles
- `GET /api/vehicle/{id}` - Vehicle details
- `GET /api/vehicle/{id}/telemetry` - Latest sensor snapshot
- `GET /api/user` - User list
- `GET /vehicle/{id}` - Full vehicle data with predictions & history
- `POST /api/agents/chat` - AI chatbot interaction
- `POST /api/service/schedule` - Book appointment
- `POST /api/login` - Authentication
- `GET /api/me` - Current user info
- `GET /dashboard` - System metrics
- `POST /admin/models/enable_claude` - Enable LLM
- `POST /admin/models/disable_llm` - Disable LLM
- `GET /admin/models/status` - LLM status
- `WS /ws/telemetry/{vehicle_id}` - Live telemetry stream

## 🔐 Security

- **JWT Authentication**: Token-based auth with interceptor
- **UEBA Monitoring**: Backend tracks all agent activities
- **CORS**: Ensure backend allows frontend origin

## 📊 Key Features Showcase

### AI-Driven Predictions
- Displayed on Profile page with:
  - Priority levels (Critical, High, Medium, Low)
  - Failure probability percentages
  - Confidence scores
  - Parts at risk
  - Recommended actions

### Real-Time Telemetry
- WebSocket connection for live sensor data
- Online/Offline status indicator
- Speed, engine temp, battery voltage display

### Service History
- Complete maintenance timeline
- Technician details
- Parts replaced
- Customer ratings (star display)
- Cost tracking

### 3D Visualization
- Three.js minimalist car model
- Smooth rotation animation
- Corporate aesthetic (no funky colors)

## 🚧 Future Enhancements

1. **UEBA Alerts View**: Display anomaly detections in Admin Panel
2. **Agent Monitor**: Live Master/Worker agent status and cycle counts
3. **User/Vehicle CRUD**: Admin forms to add/edit customers and vehicles
4. **Voice Interface**: Integrate Web Speech API for voice-based interactions
5. **Manufacturing Insights Dashboard**: RCA/CAPA visualization
6. **Fleet Management**: Multi-vehicle view for enterprise customers

## 📄 License

Private - Enterprise Use Only

