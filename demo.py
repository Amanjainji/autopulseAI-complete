"""
Demo Script - Showcases the AI Predictive Maintenance System
Run this after starting the main application
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def demo_system_overview():
    """Demo 1: System Overview"""
    print_section("📊 DEMO 1: SYSTEM OVERVIEW")
    
    response = requests.get(f"{BASE_URL}/")
    data = response.json()
    
    print(json.dumps(data, indent=2))
    print("\n✅ System is operational with all components active")

def demo_customer_and_vehicles():
    """Demo 2: Customer and Vehicle Management"""
    print_section("🚗 DEMO 2: CUSTOMER & VEHICLE DATA")
    
    # Get all customers
    response = requests.get(f"{BASE_URL}/customers")
    customers = response.json()
    
    print(f"Total Customers: {customers['total']}")
    print("\nSample Customers:")
    for customer in customers['customers'][:3]:
        print(f"  • {customer['name']} - {customer['phone']} - Vehicle: {customer['vehicle_id']}")
    
    # Get vehicle details
    print("\n" + "-"*80)
    vehicle_id = customers['customers'][0]['vehicle_id']
    response = requests.get(f"{BASE_URL}/vehicle/{vehicle_id}")
    vehicle_data = response.json()
    
    print(f"\nDetailed Vehicle Info: {vehicle_id}")
    print(json.dumps(vehicle_data['vehicle'], indent=2))

def demo_real_time_sensors():
    """Demo 3: Real-time Sensor Data"""
    print_section("📡 DEMO 3: REAL-TIME SENSOR DATA")
    
    response = requests.get(f"{BASE_URL}/vehicles")
    vehicles = response.json()
    
    vehicle_id = vehicles['vehicles'][0]['id']
    
    print(f"Fetching real-time sensor data for {vehicle_id}...")
    response = requests.get(f"{BASE_URL}/sensors/{vehicle_id}")
    sensor_data = response.json()
    
    print(json.dumps(sensor_data['data'], indent=2))
    
    # Check for issues
    data = sensor_data['data']
    issues = []
    if data['engine_temp'] > 100:
        issues.append("🔴 Engine overheating detected!")
    if data['oil_pressure'] < 30:
        issues.append("🟠 Low oil pressure!")
    if data['battery_voltage'] < 12.5:
        issues.append("🟡 Weak battery voltage!")
    
    if issues:
        print("\n⚠️ Issues Detected:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ All sensor readings within normal range")

def demo_predictions():
    """Demo 4: AI Predictions"""
    print_section("🤖 DEMO 4: AI PREDICTIVE MAINTENANCE")
    
    # Wait for agents to run
    print("Waiting for agents to analyze data (15 seconds)...")
    time.sleep(15)
    
    response = requests.get(f"{BASE_URL}/predictions")
    predictions = response.json()
    
    print(f"Total Predictions: {predictions['total']}")
    print(f"\nPredictions by Status:")
    print(json.dumps(predictions['by_status'], indent=2))
    
    if predictions['predictions']:
        print("\n📋 Sample Predictions:")
        for pred in predictions['predictions'][:5]:
            priority_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(pred['priority'], "⚪")
            
            print(f"\n  {priority_emoji} Priority: {pred['priority'].upper()}")
            print(f"     Vehicle: {pred['vehicle_id']}")
            print(f"     Issue: {pred['predicted_issue']}")
            print(f"     Confidence: {pred['confidence_score']:.1%}")
            print(f"     Status: {pred['status']}")
            print(f"     Recommended Action: {pred['recommended_action']}")

def demo_chat_agent():
    """Demo 5: Chat AI Agent"""
    print_section("💬 DEMO 5: CHAT AI AGENT")
    
    response = requests.get(f"{BASE_URL}/customers")
    customer_id = response.json()['customers'][0]['id']
    customer_name = response.json()['customers'][0]['name']
    
    print(f"Customer: {customer_name} ({customer_id})\n")
    
    # Test different intents
    test_messages = [
        "How is my car doing?",
        "I need to schedule service",
        "Show my service history",
        "What's the cost for an oil change?"
    ]
    
    for message in test_messages:
        print(f"\n{'='*40}")
        print(f"Customer: {message}")
        print(f"{'='*40}")
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"customer_id": customer_id, "message": message}
        )
        
        chat_response = response.json()
        print(f"\nAI Agent Response:\n{chat_response['response']}")
        
        time.sleep(2)

def demo_appointments():
    """Demo 6: Appointment Management"""
    print_section("📅 DEMO 6: APPOINTMENT SCHEDULING")
    
    # Wait for scheduling agent
    print("Waiting for scheduling agent to create appointments...")
    time.sleep(20)
    
    response = requests.get(f"{BASE_URL}/appointments")
    appointments = response.json()
    
    print(f"Total Appointments: {appointments['total']}")
    print(f"Scheduled: {appointments['scheduled']}")
    
    if appointments['appointments']:
        print("\n📋 Scheduled Appointments:")
        for apt in appointments['appointments'][:5]:
            print(f"\n  Appointment ID: {apt['id']}")
            print(f"  Customer: {apt['customer_id']}")
            print(f"  Vehicle: {apt['vehicle_id']}")
            print(f"  Date: {apt['appointment_date']} at {apt['appointment_time']}")
            print(f"  Service: {apt['service_type']}")
            print(f"  Priority: {apt['priority'].upper()}")
            print(f"  Location: {apt['service_center']}")
    else:
        print("\n⏳ No appointments scheduled yet. Agents are still processing...")

def demo_ueba_security():
    """Demo 7: UEBA Security Monitoring"""
    print_section("🔐 DEMO 7: UEBA SECURITY MONITORING")
    
    print("Simulating security threat...\n")
    response = requests.post(f"{BASE_URL}/ueba/simulate_threat")
    print(response.json()['message'])
    
    time.sleep(2)
    
    print("\nFetching UEBA security report...")
    response = requests.get(f"{BASE_URL}/ueba/report")
    ueba_data = response.json()
    
    print(f"\nTotal Anomalies Detected: {ueba_data['total_anomalies']}")
    
    if ueba_data['recent_anomalies']:
        print("\n⚠️ Recent Anomalous Activities:")
        for anomaly in ueba_data['recent_anomalies'][-3:]:
            print(f"\n  Agent: {anomaly['agent']}")
            print(f"  Action: {anomaly['action']}")
            print(f"  Resource: {anomaly['resource']}")
            print(f"  Anomaly Score: {anomaly['anomaly_score']:.2f}")
            print(f"  Timestamp: {anomaly['timestamp']}")
    
    print("\n📊 Agent Statistics:")
    for agent, stats in ueba_data['agent_statistics'].items():
        if stats['total_actions'] > 0:
            print(f"\n  {agent}:")
            print(f"    Total Actions: {stats['total_actions']}")
            print(f"    Anomalies: {stats['anomalies']}")
            print(f"    Anomaly Rate: {stats['anomaly_rate']}")

def demo_dashboard():
    """Demo 8: System Dashboard"""
    print_section("📊 DEMO 8: SYSTEM DASHBOARD")
    
    response = requests.get(f"{BASE_URL}/dashboard")
    dashboard = response.json()
    
    print("System Overview:")
    print(json.dumps(dashboard['system_overview'], indent=2))
    
    print("\n\nVehicle Health Distribution:")
    print(json.dumps(dashboard['vehicle_health'], indent=2))
    
    print("\n\nPredictions by Priority:")
    print(json.dumps(dashboard['predictions_by_priority'], indent=2))
    
    print("\n\nMaster Agent Status:")
    print(json.dumps(dashboard['master_agent'], indent=2))
    
    print("\n\nUEBA Security Status:")
    print(json.dumps(dashboard['ueba_security'], indent=2))

def demo_edge_cases():
    """Demo 9: Edge Cases"""
    print_section("⚡ DEMO 9: EDGE CASES HANDLING")
    
    print("Edge Case 1: Critical Failure Alert")
    print("-" * 80)
    
    # Update sensor with critical values
    critical_data = {
        "vehicle_id": "VEH001",
        "engine_temp": 112.5,
        "oil_pressure": 18.0,
        "battery_voltage": 11.2,
        "fuel_level": 5.0
    }
    
    response = requests.post(f"{BASE_URL}/sensors/update", json=critical_data)
    print(f"Updated VEH001 with critical sensor values")
    print("Waiting for agents to detect and respond...")
    time.sleep(25)
    
    # Check predictions
    response = requests.get(f"{BASE_URL}/predictions/VEH001")
    predictions = response.json()
    
    critical_preds = [p for p in predictions['predictions'] if p['priority'] == 'critical']
    if critical_preds:
        print(f"\n🔴 {len(critical_preds)} Critical issues detected!")
        for pred in critical_preds[:3]:
            print(f"  • {pred['predicted_issue']}")
    
    print("\n\nEdge Case 2: Customer Declining Appointment")
    print("-" * 80)
    print("System tracks declined appointments and schedules follow-up")
    print("Check predictions with status 'declined' in the system")
    
    print("\n\nEdge Case 3: Recurring Defect Pattern")
    print("-" * 80)
    print("Manufacturing Insights Agent identifies recurring issues")
    print("Generates RCA/CAPA reports for manufacturing team")
    print("Check console output for recurring defect alerts")

def run_full_demo():
    """Run complete demonstration"""
    print("\n" + "="*80)
    print("🚗 AI PREDICTIVE VEHICLE MAINTENANCE SYSTEM - FULL DEMO")
    print("="*80)
    print("\nThis demo will showcase all system capabilities")
    print("Make sure the main application is running at http://localhost:8000")
    print("\nPress Enter to begin...")
    input()
    
    try:
        demo_system_overview()
        time.sleep(3)
        
        demo_customer_and_vehicles()
        time.sleep(3)
        
        demo_real_time_sensors()
        time.sleep(3)
        
        demo_predictions()
        time.sleep(3)
        
        demo_chat_agent()
        time.sleep(3)
        
        demo_appointments()
        time.sleep(3)
        
        demo_ueba_security()
        time.sleep(3)
        
        demo_dashboard()
        time.sleep(3)
        
        demo_edge_cases()
        
        print("\n" + "="*80)
        print("✅ DEMO COMPLETE!")
        print("="*80)
        print("\nExplore more:")
        print("  • API Docs: http://localhost:8000/docs")
        print("  • Dashboard: GET /dashboard")
        print("  • UEBA Report: GET /ueba/report")
        print("="*80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server")
        print("Please make sure the application is running:")
        print("  python main_app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    run_full_demo()
