"""Quick route verification script"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("🔍 Testing Specific Routes\n")
print("="*60)

# Test 1: Chat endpoint
print("\n1. Testing /api/agents/chat...")
try:
    response = requests.post(
        f"{BASE_URL}/api/agents/chat",
        json={"user_id": "CUST-001", "message": "Test message"},
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ PASS - Reply: {response.json().get('reply', '')[:50]}...")
    else:
        print(f"   ❌ FAIL - {response.text}")
except Exception as e:
    print(f"   ❌ ERROR - {e}")

# Test 2: Service booking
print("\n2. Testing /api/service/schedule...")
try:
    response = requests.post(
        f"{BASE_URL}/api/service/schedule",
        json={
            "vehicle_id": "VEH001",
            "user_id": "CUST-001",
            "slot_id": "2025-10-20T10:00"
        },
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ PASS - Appointment: {data.get('appointment', {}).get('id')}")
    else:
        print(f"   ❌ FAIL - {response.text}")
except Exception as e:
    print(f"   ❌ ERROR - {e}")

# Test 3: Dashboard stats
print("\n3. Testing /dashboard/stats...")
try:
    response = requests.get(f"{BASE_URL}/dashboard/stats", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ PASS - Total vehicles: {data.get('system_overview', {}).get('total_vehicles')}")
    else:
        print(f"   ❌ FAIL - {response.text}")
except Exception as e:
    print(f"   ❌ ERROR - {e}")

# Test 4: List all routes
print("\n4. Checking available routes...")
try:
    response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
    if response.status_code == 200:
        openapi = response.json()
        paths = openapi.get("paths", {})
        print(f"   Total routes: {len(paths)}")
        print("   Key routes:")
        for path in sorted(paths.keys()):
            if any(k in path for k in ["/api/", "/dashboard", "/voice"]):
                methods = list(paths[path].keys())
                print(f"     {path} [{', '.join(m.upper() for m in methods)}]")
except Exception as e:
    print(f"   ❌ ERROR - {e}")

print("\n" + "="*60)
