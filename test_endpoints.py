"""
Comprehensive endpoint testing script for AutoPulse AI system
Tests all backend APIs, agents, and integration points
"""

import requests
import json
import time
from typing import Dict, Any, List

BASE_URL = "http://localhost:8000"

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.total = 0
    
    def add_pass(self, test_name: str, details: str = ""):
        self.passed.append((test_name, details))
        self.total += 1
        print(f"✅ PASS: {test_name}")
        if details:
            print(f"   {details}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed.append((test_name, error))
        self.total += 1
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")
    
    def summary(self):
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {self.total}")
        print(f"✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"Success Rate: {len(self.passed)/self.total*100:.1f}%")
        print("="*80 + "\n")

results = TestResults()

def test_backend_health():
    """Test 1: Backend Health & Initialization"""
    print("\n" + "="*80)
    print("🔍 TEST CATEGORY: Backend Health & Initialization")
    print("="*80 + "\n")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            results.add_pass("Backend health endpoint", 
                           f"Status: {data.get('status')}, Workers: {data['components']['worker_agents']}")
            
            # Validate response structure
            assert "system" in data
            assert "components" in data
            assert "stats" in data
            results.add_pass("Health response structure validation")
        else:
            results.add_fail("Backend health endpoint", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("Backend health endpoint", str(e))

def test_vehicle_apis():
    """Test 2: Vehicle Data APIs"""
    print("\n" + "="*80)
    print("🔍 TEST CATEGORY: Vehicle Data APIs")
    print("="*80 + "\n")
    
    try:
        # Test vehicle list
        response = requests.get(f"{BASE_URL}/api/vehicle", timeout=5)
        if response.status_code == 200:
            vehicles = response.json()
            results.add_pass("Vehicle list endpoint", f"Found {len(vehicles)} vehicles")
            
            if vehicles and len(vehicles) > 0:
                vehicle_id = vehicles[0].get("id") or vehicles[0].get("vehicle_id")
                
                # Test vehicle detail
                detail_response = requests.get(f"{BASE_URL}/api/vehicle/{vehicle_id}", timeout=5)
                if detail_response.status_code == 200:
                    vehicle = detail_response.json()
                    results.add_pass("Vehicle detail endpoint", 
                                   f"Model: {vehicle.get('model')}, Status: {vehicle.get('health_status')}")
                else:
                    results.add_fail("Vehicle detail endpoint", f"Status: {detail_response.status_code}")
                
                # Test telemetry
                telemetry_response = requests.get(f"{BASE_URL}/api/vehicle/{vehicle_id}/telemetry", timeout=5)
                if telemetry_response.status_code == 200:
                    telemetry = telemetry_response.json()
                    results.add_pass("Vehicle telemetry endpoint", 
                                   f"Status: {telemetry.get('status')}")
                else:
                    results.add_fail("Vehicle telemetry endpoint", f"Status: {telemetry_response.status_code}")
        else:
            results.add_fail("Vehicle list endpoint", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("Vehicle APIs", str(e))

def test_customer_apis():
    """Test 3: Customer Data APIs"""
    print("\n" + "="*80)
    print("🔍 TEST CATEGORY: Customer Data APIs")
    print("="*80 + "\n")
    
    try:
        # Test customer list
        response = requests.get(f"{BASE_URL}/api/user", timeout=5)
        if response.status_code == 200:
            customers = response.json()
            results.add_pass("Customer list endpoint", f"Found {len(customers)} customers")
        else:
            results.add_fail("Customer list endpoint", f"Status code: {response.status_code}")
        
        # Test customers endpoint (alias)
        response2 = requests.get(f"{BASE_URL}/customers", timeout=5)
        if response2.status_code == 200:
            data = response2.json()
            results.add_pass("Customers endpoint", f"Total: {data.get('total')}")
        else:
            results.add_fail("Customers endpoint", f"Status code: {response2.status_code}")
    except Exception as e:
        results.add_fail("Customer APIs", str(e))

def test_chat_agent():
    """Test 4: Chat Agent API"""
    print("\n" + "="*80)
    print("🔍 TEST CATEGORY: Chat Agent")
    print("="*80 + "\n")
    
    try:
        payload = {
            "user_id": "CUST-001",
            "message": "What is the status of my vehicle?"
        }
        response = requests.post(f"{BASE_URL}/api/agents/chat", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")
            results.add_pass("Chat agent endpoint", f"Reply length: {len(reply)} chars")
        else:
            results.add_fail("Chat agent endpoint", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("Chat agent endpoint", str(e))

def test_service_booking():
    """Test 5: Service Booking API"""
    print("\n" + "="*80)
    print("🔍 TEST CATEGORY: Service Booking")
    print("="*80 + "\n")
    
    try:
        payload = {
            "vehicle_id": "VEH001",
            "user_id": "CUST-001",
            "slot_id": "2025-10-20T10:00"
        }
        response = requests.post(f"{BASE_URL}/api/service/schedule", json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            appointment = data.get("appointment", {})
            results.add_pass("Service booking endpoint", 
                           f"Appointment: {appointment.get('id')}, Status: {appointment.get('status')}")
        else:
            results.add_fail("Service booking endpoint", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("Service booking endpoint", str(e))

def test_voice_agent():
    """Test 6: Voice Agent Integration"""
    print("\n" + "="*80)
    print("🔍 TEST CATEGORY: Voice Agent")
    print("="*80 + "\n")
    
    try:
        payload = {
            "customer_id": "CUST-001",
            "customer_name": "Test Customer",
            "phone": "+1-555-TEST",
            "message": "We detected a maintenance issue with your vehicle.",
            "metadata": {
                "vehicle_id": "VEH001",
                "vehicle_model": "Test Model",
                "priority": "high"
            }
        }
        response = requests.post(f"{BASE_URL}/api/voice/outbound", json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            results.add_pass("Voice agent outbound call", 
                           f"Call ID: {data.get('call_id')}, Provider: {data.get('provider')}")
        else:
            results.add_fail("Voice agent outbound call", f"Status code: {response.status_code}")
        
        # Test voice events endpoint
        events_response = requests.get(f"{BASE_URL}/api/voice/events", timeout=5)
        if events_response.status_code == 200:
            events = events_response.json()
            results.add_pass("Voice agent events endpoint", 
                           f"Events: {len(events.get('events', []))}")
        else:
            results.add_fail("Voice agent events endpoint", f"Status: {events_response.status_code}")
    except Exception as e:
        results.add_fail("Voice agent APIs", str(e))

def test_predictions():
    """Test 7: Predictions & Diagnosis"""
    print("\n" + "="*80)
    print("🔍 TEST CATEGORY: Predictions & Diagnosis")
    print("="*80 + "\n")
    
    try:
        response = requests.get(f"{BASE_URL}/predictions", timeout=5)
        if response.status_code == 200:
            data = response.json()
            predictions = data.get("predictions", [])
            results.add_pass("Predictions endpoint", f"Total: {data.get('total')}")
            
            if predictions:
                pred = predictions[0]
                results.add_pass("Prediction data structure", 
                               f"Priority: {pred.get('priority')}, Status: {pred.get('status')}")
        else:
            results.add_fail("Predictions endpoint", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("Predictions APIs", str(e))

def test_admin_endpoints():
    """Test 8: Admin & Dashboard"""
    print("\n" + "="*80)
    print("🔍 TEST CATEGORY: Admin & Dashboard")
    print("="*80 + "\n")
    
    try:
        # Test dashboard stats
        response = requests.get(f"{BASE_URL}/dashboard/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            results.add_pass("Dashboard stats endpoint", 
                           f"Total vehicles: {data.get('total_vehicles')}")
        else:
            results.add_fail("Dashboard stats endpoint", f"Status code: {response.status_code}")
        
        # Test LLM status
        llm_response = requests.get(f"{BASE_URL}/admin/models/status", timeout=5)
        if llm_response.status_code == 200:
            llm_data = llm_response.json()
            results.add_pass("LLM status endpoint", 
                           f"Provider: {llm_data.get('provider')}, Enabled: {llm_data.get('enabled')}")
        else:
            results.add_fail("LLM status endpoint", f"Status: {llm_response.status_code}")
    except Exception as e:
        results.add_fail("Admin endpoints", str(e))

def test_ueba_security():
    """Test 9: UEBA Security Monitoring"""
    print("\n" + "="*80)
    print("🔍 TEST CATEGORY: UEBA Security")
    print("="*80 + "\n")
    
    try:
        response = requests.get(f"{BASE_URL}/ueba/report", timeout=5)
        if response.status_code == 200:
            data = response.json()
            results.add_pass("UEBA anomaly report", 
                           f"Total logs: {data.get('total_logs')}, Anomalies: {data.get('total_anomalies')}")
        else:
            results.add_fail("UEBA anomaly report", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("UEBA endpoints", str(e))

def main():
    print("\n" + "="*80)
    print("🧪 AUTOPULSE AI - COMPREHENSIVE ENDPOINT TESTING")
    print("="*80)
    print(f"Target: {BASE_URL}")
    print("="*80 + "\n")
    
    # Run all test categories
    test_backend_health()
    test_vehicle_apis()
    test_customer_apis()
    test_chat_agent()
    test_service_booking()
    test_voice_agent()
    test_predictions()
    test_admin_endpoints()
    test_ueba_security()
    
    # Print summary
    results.summary()
    
    # Return exit code
    return 0 if len(results.failed) == 0 else 1

if __name__ == "__main__":
    exit(main())
