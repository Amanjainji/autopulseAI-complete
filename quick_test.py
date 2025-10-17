"""Quick route test - runs fast before server shuts down"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def quick_test():
    tests = []
    
    # Test 1: Chat
    try:
        r = requests.post(f"{BASE_URL}/api/agents/chat", 
                         json={"user_id": "CUST-001", "message": "Status?"}, timeout=3)
        tests.append(("Chat", r.status_code == 200, r.status_code))
    except Exception as e:
        tests.append(("Chat", False, str(e)[:50]))
    
    # Test 2: Booking
    try:
        r = requests.post(f"{BASE_URL}/api/service/schedule",
                         json={"vehicle_id": "VEH001", "user_id": "CUST-001", "slot_id": "2025-10-20T10:00"}, timeout=3)
        tests.append(("Booking", r.status_code == 200, r.status_code))
    except Exception as e:
        tests.append(("Booking", False, str(e)[:50]))
    
    # Test 3: Dashboard
    try:
        r = requests.get(f"{BASE_URL}/dashboard/stats", timeout=3)
        tests.append(("Dashboard", r.status_code == 200, r.status_code))
    except Exception as e:
        tests.append(("Dashboard", False, str(e)[:50]))
    
    print("\n" + "="*60)
    print("🔍 QUICK ROUTE TEST")
    print("="*60)
    for name, passed, info in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name:12} | {info}")
    print("="*60 + "\n")
    
    all_passed = all(t[1] for t in tests)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(quick_test())
