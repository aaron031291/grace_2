"""Test validation error response"""
import requests
import json

# Test endpoint that triggers validation without auth
# Use a simple test case
print("Testing validation error response...")

# Try to trigger a validation error (invalid query parameter type)
try:
    response = requests.get(
        "http://127.0.0.1:8000/api/verification/audit?limit=invalid_number"
    )
    
    print(f"Status: {response.status_code}")
    print(f"\nResponse:\n{json.dumps(response.json(), indent=2)}")
    
    # Check if execution_trace is present
    data = response.json()
    if "execution_trace" in data:
        print("\n[OK] execution_trace is present!")
        print(f"Steps: {len(data['execution_trace'].get('steps', []))}")
    else:
        print("\n[MISSING] execution_trace is missing!")
        
    if "data_provenance" in data:
        print("[OK] data_provenance is present!")
    else:
        print("[MISSING] data_provenance is missing!")
        
    if "suggestions" in data:
        print(f"[OK] suggestions present: {data['suggestions']}")
    else:
        print("[MISSING] suggestions missing!")
        
except Exception as e:
    print(f"Error: {e}")
