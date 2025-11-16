"""Setup script for Business Empire System

Run this to configure API keys and test the system.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from backend.secrets_vault import secrets_vault
from backend.transcendence.business.payment_processor import payment_processor
from backend.transcendence.business.marketplace_connector import marketplace_connector


async def setup_stripe():
    """Setup Stripe API keys"""
    print("\n🔑 Stripe Setup")
    print("-" * 50)
    
    api_key = input("Enter Stripe API key (sk_test_... or sk_live_...): ").strip()
    
    if not api_key:
        print("⚠️  Skipping Stripe setup (no key provided)")
        return False
    
    if not (api_key.startswith("sk_test_") or api_key.startswith("sk_live_")):
        print("❌ Invalid Stripe key format")
        return False
    
    environment = "test" if api_key.startswith("sk_test_") else "production"
    
    result = await secrets_vault.store_stripe_key(
        api_key=api_key,
        owner="aaron",
        environment=environment
    )
    
    print(f"✅ Stripe API key stored ({environment})")
    
    # Optional: webhook secret
    webhook_secret = input("Enter Stripe webhook secret (whsec_...) [optional]: ").strip()
    
    if webhook_secret:
        await secrets_vault.store_secret(
            secret_key="stripe_webhook_secret",
            secret_value=webhook_secret,
            secret_type="password",
            owner="aaron",
            service="stripe",
            description="Stripe webhook signing secret"
        )
        print("✅ Webhook secret stored")
    
    return True


async def setup_upwork():
    """Setup Upwork OAuth token"""
    print("\n🔑 Upwork Setup")
    print("-" * 50)
    
    oauth_token = input("Enter Upwork OAuth token [optional]: ").strip()
    
    if not oauth_token:
        print("⚠️  Skipping Upwork setup (no token provided)")
        return False
    
    result = await secrets_vault.store_upwork_credentials(
        oauth_token=oauth_token,
        owner="aaron"
    )
    
    print("✅ Upwork OAuth token stored")
    return True


async def test_stripe():
    """Test Stripe connection"""
    print("\n🧪 Testing Stripe Connection")
    print("-" * 50)
    
    # Try to create a test invoice
    result = await payment_processor.create_invoice(
        project_id=1,
        amount=100.0,
        description="Test invoice - Business Empire Setup",
        client_id="test_client"
    )
    
    if result.get("success"):
        print("✅ Stripe connection successful!")
        print(f"   Invoice ID: {result['invoice_id']}")
        print(f"   Amount: ${result['amount']}")
        print(f"   URL: {result['hosted_invoice_url']}")
        return True
    else:
        print(f"❌ Stripe test failed: {result.get('error')}")
        return False


async def test_upwork():
    """Test Upwork connection"""
    print("\n🧪 Testing Upwork Connection")
    print("-" * 50)
    
    # Try to search jobs
    jobs = await marketplace_connector.search_jobs(
        keywords="python developer",
        budget_min=500,
        limit=5
    )
    
    if jobs:
        print(f"✅ Upwork connection successful! Found {len(jobs)} jobs")
        for i, job in enumerate(jobs[:3], 1):
            print(f"   {i}. {job['title']} - ${job.get('budget', 'N/A')}")
        return True
    else:
        print("⚠️  No jobs found (might be connection issue or no matches)")
        return False


async def show_status():
    """Show current configuration status"""
    print("\n📊 Current Configuration Status")
    print("-" * 50)
    
    # Check Stripe
    stripe_key = await secrets_vault.retrieve_secret(
        key="stripe_api_key",
        accessor="setup_script",
        purpose="status_check"
    )
    
    if stripe_key:
        env = "test" if stripe_key.startswith("sk_test_") else "production"
        print(f"✅ Stripe: Configured ({env})")
    else:
        print("❌ Stripe: Not configured")
    
    # Check Upwork
    upwork_token = await secrets_vault.retrieve_secret(
        key="upwork_oauth_token",
        accessor="setup_script",
        purpose="status_check"
    )
    
    if upwork_token:
        print("✅ Upwork: Configured")
    else:
        print("❌ Upwork: Not configured")
    
    # List all secrets
    secrets = await secrets_vault.list_secrets()
    print(f"\n📋 Total secrets stored: {len(secrets)}")


async def main():
    """Main setup flow"""
    print("=" * 50)
    print("🚀 GRACE Business Empire Setup")
    print("=" * 50)
    
    print("\nThis script will help you configure:")
    print("  1. Stripe payment processing")
    print("  2. Upwork marketplace integration")
    print("  3. Fiverr integration (optional)")
    
    choice = input("\nContinue with setup? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("Setup cancelled.")
        return
    
    # Setup Stripe
    stripe_configured = await setup_stripe()
    
    # Setup Upwork
    upwork_configured = await setup_upwork()
    
    # Run tests
    if stripe_configured:
        test_stripe_choice = input("\nTest Stripe connection? (y/n): ").strip().lower()
        if test_stripe_choice == 'y':
            await test_stripe()
    
    if upwork_configured:
        test_upwork_choice = input("\nTest Upwork connection? (y/n): ").strip().lower()
        if test_upwork_choice == 'y':
            await test_upwork()
    
    # Show final status
    await show_status()
    
    print("\n" + "=" * 50)
    print("✅ Setup Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("  1. Read BUSINESS_EXECUTION.md for full guide")
    print("  2. Run tests: pytest tests/test_payment_marketplace.py -v")
    print("  3. Start the backend: python -m uvicorn backend.main:app --reload")
    print("  4. Access API docs: http://localhost:8000/docs")
    print("\nAPI Endpoints:")
    print("  • POST /api/business/payments/invoice")
    print("  • POST /api/business/marketplace/search")
    print("  • GET  /api/business/marketplace/jobs")
    print("\n💰 Ready to start earning!")


if __name__ == "__main__":
    asyncio.run(main())
