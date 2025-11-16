"""
Approve all pending consent requests for Grace to start
"""
import asyncio
import httpx

async def approve_all():
    base_url = "http://localhost:8017"
    
    print("🔍 Fetching pending approvals...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Get pending consents
            response = await client.get(
                f"{base_url}/api/secrets/consent/pending",
                params={"user_id": "admin"}
            )
            
            if response.status_code != 200:
                print("❌ Grace might not be running yet")
                print("   Start Grace first: python serve.py")
                return
            
            data = response.json()
            pending = data.get("pending_consents", [])
            
            print(f"📋 Found {len(pending)} pending approvals")
            
            if len(pending) == 0:
                print("✅ No approvals needed!")
                return
            
            # Approve each one
            approved = 0
            for consent in pending:
                consent_id = consent.get("consent_id")
                secret_key = consent.get("secret_key", "unknown")
                
                print(f"  ✓ Approving: {secret_key} ({consent_id})")
                
                approve_response = await client.post(
                    f"{base_url}/api/secrets/consent/respond",
                    json={
                        "consent_id": consent_id,
                        "approved": True,
                        "user_id": "admin",
                        "approval_method": "script"
                    }
                )
                
                if approve_response.status_code == 200:
                    approved += 1
                else:
                    print(f"    ⚠️ Failed to approve {consent_id}")
            
            print(f"\n✅ Approved {approved}/{len(pending)} requests")
            print("🚀 Grace is now ready!")
            
    except httpx.ConnectError:
        print("\n❌ Cannot connect to Grace")
        print("   Please start Grace first: python serve.py")
        print("   Then run this script in another terminal")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(approve_all())
