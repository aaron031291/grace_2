"""Demo Script for Revenue Tracking and Dashboards

Run this to populate test data and see the dashboards in action.
"""

import asyncio
from backend.transcendence.business.revenue_tracker import revenue_tracker
from backend.models import async_session, Base, engine


async def seed_demo_data():
    """Create demo revenue and expense data"""
    print("\n" + "="*60)
    print("SEEDING DASHBOARD DEMO DATA")
    print("="*60 + "\n")
    
    # Create tables
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Tables created\n")
    
    # Add revenue
    print("Adding revenue transactions...")
    
    revenues = [
        ("AI Consulting", 15000, "consulting", "CLIENT-001", "Website AI integration"),
        ("AI Consulting", 12000, "consulting", "CLIENT-002", "Chatbot development"),
        ("AI Consulting", 18000, "consulting", "CLIENT-003", "ML model training"),
        ("SaaS Platform", 5000, "saas", None, "Monthly subscriptions"),
        ("SaaS Platform", 6000, "saas", None, "Monthly subscriptions"),
        ("Trading Bot", 3000, "trading", None, "Automated trading profits"),
        ("Trading Bot", 2500, "trading", None, "Automated trading profits"),
        ("Content Creation", 4000, "content", "CLIENT-004", "Blog posts and videos"),
        ("Freelance Work", 2000, "freelance", "CLIENT-005", "Various small projects"),
        ("Affiliate Marketing", 1500, "affiliate", None, "Referral commissions"),
    ]
    
    for source, amount, category, client_id, description in revenues:
        result = await revenue_tracker.track_income(
            source=source,
            amount=amount,
            category=category,
            client_id=client_id,
            description=description
        )
        print(f"  ✓ {source}: ${amount}")
    
    print(f"\n✓ Added {len(revenues)} revenue transactions\n")
    
    # Add expenses
    print("Adding expense transactions...")
    
    expenses = [
        ("hosting", 500, "AWS cloud hosting", "Amazon Web Services"),
        ("hosting", 200, "Domain registration", "Namecheap"),
        ("marketing", 1500, "Google Ads campaign", "Google"),
        ("marketing", 800, "Social media ads", "Meta"),
        ("tools", 300, "Software licenses", "Various"),
        ("tools", 150, "API subscriptions", "OpenAI"),
        ("salary", 5000, "Contractor payments", "Freelancer"),
        ("operations", 400, "Office supplies", "Amazon"),
        ("operations", 250, "Communication tools", "Slack"),
        ("legal", 800, "Business registration", "LegalZoom"),
    ]
    
    for category, amount, description, vendor in expenses:
        result = await revenue_tracker.track_expense(
            category=category,
            amount=amount,
            description=description,
            vendor=vendor
        )
        print(f"  ✓ {category}: ${amount}")
    
    print(f"\n✓ Added {len(expenses)} expense transactions\n")
    
    # Calculate metrics
    print("Calculating business metrics...")
    
    profit = await revenue_tracker.calculate_profit("month")
    print(f"\n📊 PROFIT SUMMARY (This Month):")
    print(f"  Revenue:  ${profit['revenue']:,.2f}")
    print(f"  Expenses: ${profit['expenses']:,.2f}")
    print(f"  Profit:   ${profit['profit']:,.2f}")
    print(f"  Margin:   {profit['profit_margin']:.1f}%\n")
    
    # Analyze sources
    print("Analyzing revenue sources...")
    sources = await revenue_tracker.analyze_revenue_sources()
    
    print(f"\n💰 TOP REVENUE SOURCES:")
    for i, source in enumerate(sources[:5], 1):
        print(f"  {i}. {source['source']}")
        print(f"     Revenue: ${source['total_revenue']:,.2f}")
        print(f"     Transactions: {source['transaction_count']}")
        print(f"     Avg/Transaction: ${source['avg_transaction']:,.2f}\n")
    
    # Growth rate
    print("Calculating growth rate...")
    growth = await revenue_tracker.calculate_growth_rate("month")
    
    print(f"📈 GROWTH RATE:")
    print(f"  Current:  ${growth['current_revenue']:,.2f}")
    print(f"  Previous: ${growth['previous_revenue']:,.2f}")
    print(f"  Growth:   {growth['growth_rate']:.1f}% {growth['growth_direction']}\n")
    
    # Forecasts
    print("Generating revenue forecasts...")
    forecasts = await revenue_tracker.forecast_revenue(months_ahead=3)
    
    if forecasts:
        print(f"\n🔮 REVENUE FORECASTS:")
        for forecast in forecasts:
            print(f"  {forecast['month']}: ${forecast['predicted_revenue']:,.2f}")
            print(f"    Confidence: {forecast['confidence']*100:.0f}%\n")
    
    # Optimizations
    print("Generating Grace's optimization suggestions...")
    suggestions = await revenue_tracker.suggest_optimizations()
    
    print(f"\n🎯 GRACE'S SUGGESTIONS ({len(suggestions)}):")
    for i, sugg in enumerate(suggestions, 1):
        print(f"\n  {i}. {sugg['title']}")
        print(f"     Type: {sugg['type']}")
        print(f"     Confidence: {sugg.get('confidence', 0)*100:.0f}%")
        if 'expected_increase' in sugg and sugg['expected_increase'] > 0:
            print(f"     Expected Increase: ${sugg['expected_increase']:,.2f}")
        if 'cost' in sugg and sugg['cost'] > 0:
            print(f"     Cost: ${sugg['cost']:,.2f}")
        if 'roi' in sugg and sugg['roi'] > 0:
            print(f"     ROI: {sugg['roi']*100:.0f}%")
    
    print("\n" + "="*60)
    print("DEMO DATA SEEDED SUCCESSFULLY!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start the backend: cd grace_rebuild && python -m backend.main")
    print("2. Start the frontend: cd grace-frontend && npm run dev")
    print("3. Open dashboard: http://localhost:5173")
    print("4. Navigate to Transcendence Dashboard")
    print("5. Explore COGNITIVE, BUSINESS, and PROPOSALS tabs")
    print("\n")


async def main():
    """Run demo"""
    await seed_demo_data()


if __name__ == "__main__":
    asyncio.run(main())
