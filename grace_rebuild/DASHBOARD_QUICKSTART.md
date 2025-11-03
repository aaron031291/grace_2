# Dashboard Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Seed Demo Data
```bash
run_dashboard_demo.bat
```
Or manually:
```bash
py demo_dashboards.py
```

This creates:
- 10 revenue transactions ($69,000 total)
- 10 expense transactions ($9,900 total)
- Profit calculation ($59,100)
- Revenue source analysis
- Growth metrics
- ML forecasts
- Optimization suggestions

### Step 2: Start Backend
```bash
start_backend.bat
```
Or manually:
```bash
cd grace_rebuild
py -m backend.main
```

Backend will start on: `http://localhost:8000`

### Step 3: Start Frontend
```bash
cd grace-frontend
npm run dev
```

Frontend will start on: `http://localhost:5173`

### Step 4: View Dashboards
Open browser to: `http://localhost:5173`

Navigate to: **Transcendence Dashboard**

## 📊 Dashboard Tabs

### COGNITIVE Tab
Watch Grace think in real-time:
- Current thinking stage
- Reasoning process
- Confidence levels
- Evidence and alternatives
- Real-time WebSocket updates

### BUSINESS Tab
Complete financial overview:
- Revenue: $69,000
- Expenses: $9,900
- Profit: $59,100 (85% margin!)
- Growth rate
- Top revenue sources:
  1. AI Consulting - $45,000
  2. SaaS Platform - $11,000
  3. Trading Bot - $5,500
  4. Content Creation - $4,000
  5. Freelance Work - $2,000

### PROPOSALS Tab
Grace's pending proposals:
- Review suggestions
- Approve/reject
- See impact scores
- Vote democratically

## 🧪 Run Tests
```bash
run_dashboard_tests.bat
```
Or manually:
```bash
py tests\test_dashboards.py
```

Expected output:
```
DASHBOARD & REVENUE TRACKING TESTS
====================================
✓ Track Income
✓ Track Expense
✓ Calculate Profit
✓ Analyze Revenue Sources
✓ Calculate Growth Rate
✓ Revenue Forecast
✓ Optimization Suggestions
✓ Dashboard Cognitive State
✓ Dashboard Reasoning Chains
✓ Dashboard Memory Formation
✓ Dashboard Proposals
✓ Business Metrics Update

RESULTS: 12 passed, 0 failed
```

## 📡 API Endpoints

### Revenue Tracking
```http
# Track income
POST http://localhost:8000/api/business/revenue/track
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "source": "Consulting",
  "amount": 5000,
  "category": "consulting",
  "client_id": "CLIENT-001",
  "description": "Website development"
}

# Track expense
POST http://localhost:8000/api/business/revenue/expense
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "category": "hosting",
  "amount": 200,
  "description": "AWS costs"
}

# Get profit
GET http://localhost:8000/api/business/revenue/profit?timeframe=month
Authorization: Bearer YOUR_TOKEN

# Get revenue sources
GET http://localhost:8000/api/business/revenue/sources
Authorization: Bearer YOUR_TOKEN

# Get forecast
GET http://localhost:8000/api/business/revenue/forecast?months=3
Authorization: Bearer YOUR_TOKEN

# Get optimizations
GET http://localhost:8000/api/business/revenue/optimizations
Authorization: Bearer YOUR_TOKEN
```

### Dashboard
```http
# Get cognitive state
GET http://localhost:8000/api/dashboard/cognitive/current
Authorization: Bearer YOUR_TOKEN

# Get reasoning chains
GET http://localhost:8000/api/dashboard/cognitive/reasoning?limit=10
Authorization: Bearer YOUR_TOKEN

# Get business metrics
GET http://localhost:8000/api/dashboard/business/revenue?timeframe=month
Authorization: Bearer YOUR_TOKEN

# WebSocket (real-time)
WS ws://localhost:8000/api/dashboard/ws/cognitive?token=YOUR_TOKEN
```

## 🎯 Quick Actions

### Add Your First Revenue
```python
from backend.transcendence.business.revenue_tracker import revenue_tracker

result = await revenue_tracker.track_income(
    source="Your Business",
    amount=10000.0,
    category="consulting",
    client_id="CLIENT-001"
)
```

### Add Your First Expense
```python
result = await revenue_tracker.track_expense(
    category="hosting",
    amount=500.0,
    description="Server costs"
)
```

### Get Profit
```python
profit = await revenue_tracker.calculate_profit("month")
print(f"Profit: ${profit['profit']}")
print(f"Margin: {profit['profit_margin']}%")
```

### Get Grace's Suggestions
```python
suggestions = await revenue_tracker.suggest_optimizations()
for sugg in suggestions:
    print(f"- {sugg['title']} ({sugg['type']})")
```

## 💡 Pro Tips

1. **Demo Data**: Run `demo_dashboards.py` to see the system in action
2. **Real-Time**: COGNITIVE tab updates every second via WebSocket
3. **Timeframes**: Switch between day/week/month/quarter/year views
4. **Top Sources**: Focus on businesses with highest revenue
5. **Forecasts**: Based on ML using temporal reasoning
6. **Optimizations**: Grace learns which suggestions you approve
7. **Confidence**: Higher = more certain, lower = exploring
8. **ROI**: Return on Investment for marketing suggestions
9. **Growth**: Monitor month-over-month for trends
10. **Profit Margin**: >30% is excellent, <10% needs work

## 🐛 Troubleshooting

### Backend won't start
- Check port 8000 is available
- Install requirements: `pip install -r requirements.txt`
- Check database: `grace.db` should exist

### Frontend won't start
- Install dependencies: `npm install`
- Check port 5173 is available
- Verify backend is running

### No data in dashboard
- Run demo script: `run_dashboard_demo.bat`
- Check backend logs
- Verify API endpoints return data

### WebSocket disconnected
- Check backend is running
- Verify token in localStorage
- Refresh browser

### Tests failing
- Ensure database exists
- Run from grace_rebuild directory
- Check Python version (3.8+)

## 📚 Documentation

- **Full Guide**: `DASHBOARD_GUIDE.md`
- **Delivery Report**: `DASHBOARD_DELIVERY.md`
- **Architecture**: See files in `backend/transcendence/`

## 🎉 Success!

You should now see:
- ✓ Complete financial tracking
- ✓ Real-time cognitive observatory
- ✓ Beautiful business metrics
- ✓ Grace's optimization suggestions
- ✓ ML-based revenue forecasting
- ✓ WebSocket live updates
- ✓ Proposal management

**Grace is now fully financially intelligent and observable!** 🧠💰📊
