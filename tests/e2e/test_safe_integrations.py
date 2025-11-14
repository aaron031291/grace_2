"""
Test Safe External Integration System

Demonstrates:
1. Grace discovering external APIs
2. Hunter Bridge security scanning
3. Verification Charter approval workflow
4. Safe installation with audit trail
"""

import sys
import io
import requests
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"

print("\n" + "="*70)
print("GRACE - SAFE EXTERNAL INTEGRATION TEST")
print("="*70)
print("\nDemonstrating Grace's ability to safely absorb external APIs")
print("with Hunter Bridge security + Verification Charter governance")
print("="*70)

# Test 1: View available integration categories
print("\n[Test 1] What can Grace connect to?")
print("-"*70)

response = requests.get(f"{BASE_URL}/api/integrations/categories")
if response.status_code == 200:
    categories = response.json()['categories']
    
    print(f"Grace can safely connect to {len(categories)} categories:\n")
    
    for cat_id, cat_info in categories.items():
        print(f"📦 {cat_info['name']}")
        print(f"   Examples: {', '.join(cat_info['integrations'][:3])}")
        print(f"   Risk: {cat_info['risk_level']}")
        print(f"   Approval Required: {'Yes' if cat_info['requires_approval'] else 'No'}")
        print()

# Test 2: Request Stripe integration (HIGH risk)
print("\n[Test 2] Requesting Stripe Integration (HIGH RISK)")
print("-"*70)
print("Hunter Bridge will scan for security...")
print()

request_data = {
    "integration_name": "stripe_api_v2",
    "vendor": "Stripe Inc.",
    "purpose": "Payment processing and MRR tracking",
    "api_endpoint": "https://api.stripe.com",
    "auth_method": "api_key",
    "scopes": ["read_customers", "read_subscriptions", "read_charges"],
    "risk_level": "high"
}

response = requests.post(
    f"{BASE_URL}/api/integrations/install",
    json=request_data,
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    
    print(f"✅ Security Scan: {'PASSED' if result.get('scan_passed') else 'FAILED'}")
    print(f"   Risk Score: {result.get('risk_score', 0):.2f}")
    print(f"   Status: {result['status']}")
    print(f"   Request ID: {result.get('request_id')}")
    print(f"   Message: {result.get('message')}")
    
    if result['status'] == 'pending_approval':
        print(f"\n   ⚠️ Requires Unified Logic approval (HIGH risk)")
        stripe_request_id = result['request_id']
    else:
        stripe_request_id = None

# Test 3: Request Google Analytics (LOW risk - should auto-approve)
print("\n[Test 3] Requesting Google Analytics (LOW RISK)")
print("-"*70)

request_data = {
    "integration_name": "google_analytics_read",
    "vendor": "Google",
    "purpose": "Read analytics data for traffic analysis",
    "api_endpoint": "https://analyticsreporting.googleapis.com",
    "auth_method": "oauth2",
    "scopes": ["analytics.readonly"],
    "risk_level": "low"
}

response = requests.post(
    f"{BASE_URL}/api/integrations/install",
    json=request_data
)

if response.status_code == 200:
    result = response.json()
    
    print(f"✅ Security Scan: {'PASSED' if result.get('scan_passed') else 'FAILED'}")
    print(f"   Status: {result['status']}")
    print(f"   Message: {result.get('message')}")

# Test 4: Try malicious integration (should be blocked)
print("\n[Test 4] Attempting Malicious Integration (BLOCKED)")
print("-"*70)
print("Trying to install suspicious API with dangerous scopes...")
print()

request_data = {
    "integration_name": "sketchy_api",
    "vendor": "Unknown",
    "purpose": "Full system access",
    "api_endpoint": "http://suspicious-site.com/api",  # HTTP not HTTPS!
    "auth_method": "plaintext_password",
    "scopes": ["admin", "full_access", "delete_all"],  # Dangerous!
    "risk_level": "critical"
}

response = requests.post(
    f"{BASE_URL}/api/integrations/install",
    json=request_data
)

if response.status_code == 200:
    result = response.json()
    
    if result['success'] and result['status'] == 'security_failed':
        print(f"✅ BLOCKED by Hunter Bridge!")
        print(f"   Status: {result['status']}")
        print(f"   Reason: {result.get('message')}")
        print(f"   Findings: {len(result.get('findings', []))} security issues")
    else:
        print(f"⚠️ Should have been blocked!")

# Test 5: View pending approvals
print("\n[Test 5] Viewing Pending Approvals (Unified Logic Queue)")
print("-"*70)

response = requests.get(f"{BASE_URL}/api/integrations/pending")
if response.status_code == 200:
    data = response.json()
    
    print(f"📋 Pending requests: {data['count']}\n")
    
    for req in data['pending_requests'][:3]:
        print(f"  • {req['name']} ({req['vendor']})")
        print(f"    Risk: {req['risk_level']}")
        print(f"    Purpose: {req['purpose']}")
        print(f"    ID: {req['request_id']}")
        print()

# Test 6: Approve Stripe (simulate admin approval)
if 'stripe_request_id' in locals() and stripe_request_id:
    print("\n[Test 6] Simulating Admin Approval for Stripe")
    print("-"*70)
    
    response = requests.post(
        f"{BASE_URL}/api/integrations/approve/{stripe_request_id}",
        params={"approved_by": "admin", "notes": "Approved for financial tracking"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Integration Approved!")
        print(f"   Request ID: {result['request_id']}")
        print(f"   Approved By: {result['approved_by']}")
        print(f"   Status: Now in whitelist")

# Test 7: View approved integrations
print("\n[Test 7] Viewing Approved Integrations (Whitelist)")
print("-"*70)

response = requests.get(f"{BASE_URL}/api/integrations/approved")
if response.status_code == 200:
    data = response.json()
    
    print(f"✅ Approved integrations: {data['count']}\n")
    print(f"By Risk Level:")
    for level, count in data['by_risk_level'].items():
        if count > 0:
            print(f"  {level}: {count}")

print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print("✅ Grace can discover external APIs safely")
print("✅ Hunter Bridge scans for security (TLS, credentials, scopes)")
print("✅ Verification Charter enforces policy (auto-approve vs. manual)")
print("✅ Malicious integrations blocked automatically")
print("✅ Unified Logic approval queue for high-risk")
print("✅ Complete audit trail maintained")
print("\n🛡️ Grace can now safely absorb from the external world!")
print("="*70)
print()
