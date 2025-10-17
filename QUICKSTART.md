# 🚀 Quick Start Guide

## Installation (3 Steps)

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Start the Server
```powershell
python main_app.py
```

You should see:
```
🚗 AI PREDICTIVE VEHICLE MAINTENANCE SYSTEM
Starting server...
✅ Loaded 10 customers
✅ Loaded 10 vehicles
🤖 Initializing Worker Agents...
✅ SYSTEM INITIALIZATION COMPLETE
```

### Step 3: Run the Demo (Optional)
Open a new terminal:
```powershell
python demo.py
```

## 🔗 Access Points

- **API Documentation**: http://localhost:8000/docs
- **System Status**: http://localhost:8000/
- **Dashboard**: http://localhost:8000/dashboard

## 🎯 Quick Tests

### Test 1: Check System
```powershell
curl http://localhost:8000/
```

### Test 2: View Vehicles
```powershell
curl http://localhost:8000/vehicles
```

### Test 3: Chat with AI
```powershell
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{\"customer_id\":\"CUST001\",\"message\":\"How is my car?\"}'
```

### Test 4: View Predictions
```powershell
curl http://localhost:8000/predictions
```

### Test 5: UEBA Security Report
```powershell
curl http://localhost:8000/ueba/report
```

## 📊 What Happens Automatically

Once the server starts, the Master Agent automatically:

1. **Every 20 seconds**, runs all worker agents in sequence
2. **Analyzes** vehicle sensor data for issues
3. **Predicts** maintenance needs with confidence scores
4. **Contacts** customers with personalized messages
5. **Schedules** appointments based on priority
6. **Collects** feedback from completed services
7. **Identifies** recurring defect patterns
8. **Monitors** all agent activities for security anomalies

## 🔍 Watch the Console

You'll see real-time output like:

```
🔄 Orchestration Cycle #1 - 10:30:15
================================================================================

🔍 [DataAnalysisAgent] Starting analysis...
   ⚠️ Vehicle Tesla Model S (VEH001): Engine overheating detected

🩺 [DiagnosisAgent] Running diagnostics...
   🔴 CRITICAL - Tesla Model S: Engine overheating detected
      Failure Probability: 85% | Confidence: 92%

💬 [CustomerEngagementAgent] Reaching out to customers...
   📱 Contacting John Smith (+1-555-1001)
   🚗 Vehicle: Tesla Model S (ABC0001)
   📋 Issue: Engine overheating detected (Priority: critical)

📅 [SchedulingAgent] Managing appointments...
   ✅ John Smith: 2025-10-17 at 09:00 AM (CRITICAL)

📊 [FeedbackAgent] Collecting feedback...
   ⭐ Sarah Johnson: 5/5 for Oil Change

🏭 [ManufacturingInsightsAgent] Analyzing defect patterns...
   🔧 Recurring Defect Alert:
      Model: Tesla Model S
      Issue: Engine overheating detected
      Root Cause: Inadequate cooling system capacity

✅ Orchestration Cycle #1 Complete
```

## 🧪 Testing Features

### Test Chat Agent
Visit http://localhost:8000/docs and try the `/chat` endpoint with messages like:
- "How is my car doing?"
- "I need to schedule service"
- "Show my service history"
- "What's the cost?"

### Test UEBA Security
Simulate a security threat:
```powershell
curl -X POST http://localhost:8000/ueba/simulate_threat
```

Then check the report:
```powershell
curl http://localhost:8000/ueba/report
```

### Test Predictions
After 30-60 seconds, check predictions:
```powershell
curl http://localhost:8000/predictions
```

## 🐛 Troubleshooting

### Server won't start?
- Check if port 8000 is available
- Try: `python main_app.py --port 8080`

### No predictions appearing?
- Wait 30-60 seconds for agents to run
- Check sensor data has issues: `GET /sensors/{vehicle_id}`

### Chat agent not responding?
- Verify customer_id exists: `GET /customers`
- Check console for errors

## 📚 Next Steps

1. **Explore API Docs**: http://localhost:8000/docs - Interactive API testing
2. **Run Full Demo**: `python demo.py` - Comprehensive walkthrough
3. **Read README.md**: Detailed system architecture and features
4. **Check Dashboard**: `GET /dashboard` - System statistics

## 💡 Tips

- The system generates **10 sample vehicles** on startup
- **Master Agent** runs orchestration every 20 seconds
- **UEBA** monitors all agent activities automatically
- **Chat Agent** provides personalized responses based on vehicle data
- **Predictions** are created based on sensor analysis

## 🎉 You're Ready!

The system is now running a complete AI-powered predictive maintenance ecosystem with:
- ✅ Master-Worker agent architecture
- ✅ Real-time vehicle monitoring
- ✅ Predictive failure analysis
- ✅ Customer engagement automation
- ✅ UEBA security monitoring
- ✅ Manufacturing feedback loop

Enjoy exploring! 🚗💨
