"""Revenue Tracker - Complete Financial Tracking System

Tracks income, expenses, profits, forecasts revenue using ML,
analyzes revenue sources, and suggests optimizations.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, ForeignKey, select, func
from sqlalchemy.sql import func as sql_func
from collections import defaultdict
import statistics

from ...models import Base, async_session
from ...temporal_reasoning import TemporalReasoner

class RevenueTransaction(Base):
    """Record of all revenue"""
    __tablename__ = "revenue_transactions"
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(128), unique=True, nullable=False)
    
    # Revenue details
    amount = Column(Float, nullable=False)
    source = Column(String(128), nullable=False)  # Which business/service
    category = Column(String(64), nullable=False)  # consulting, saas, trading, etc
    client_id = Column(String(128), nullable=True)  # Link to client
    
    # Metadata
    description = Column(Text, nullable=True)
    payment_method = Column(String(64), nullable=True)
    invoice_id = Column(String(128), nullable=True)
    
    # Status
    status = Column(String(32), default="completed")  # pending, completed, refunded
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    transaction_date = Column(DateTime(timezone=True), server_default=sql_func.now())


class Expense(Base):
    """Record of all expenses"""
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True)
    expense_id = Column(String(128), unique=True, nullable=False)
    
    # Expense details
    amount = Column(Float, nullable=False)
    category = Column(String(64), nullable=False)  # hosting, marketing, tools, salary, etc
    description = Column(Text, nullable=False)
    
    # Metadata
    vendor = Column(String(128), nullable=True)
    receipt_url = Column(String(512), nullable=True)
    
    # Status
    status = Column(String(32), default="completed")  # pending, completed, disputed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    expense_date = Column(DateTime(timezone=True), server_default=sql_func.now())


class RevenueForecast(Base):
    """ML-based revenue forecasts"""
    __tablename__ = "revenue_forecasts"
    
    id = Column(Integer, primary_key=True)
    forecast_id = Column(String(128), unique=True, nullable=False)
    
    # Forecast
    predicted_amount = Column(Float, nullable=False)
    timeframe = Column(String(64), nullable=False)  # "2024-01", "Q1-2024"
    confidence = Column(Float, nullable=False)
    
    # Model info
    model_used = Column(String(64), nullable=False)
    features_used = Column(JSON, default=list)
    
    # Actual results (filled in later)
    actual_amount = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    forecast_for_date = Column(DateTime(timezone=True), nullable=False)


class BusinessMetrics(Base):
    """Aggregated metrics per business/source"""
    __tablename__ = "business_metrics"
    
    id = Column(Integer, primary_key=True)
    metric_id = Column(String(128), unique=True, nullable=False)
    
    # Business identification
    business_name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)
    
    # Metrics
    revenue = Column(Float, default=0.0)
    expenses = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    growth_rate = Column(Float, default=0.0)  # Percentage
    
    # Counts
    transaction_count = Column(Integer, default=0)
    client_count = Column(Integer, default=0)
    
    # Period
    period = Column(String(64), nullable=False)  # "2024-01", "Q1-2024", "2024"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=sql_func.now())


class RevenueOptimization(Base):
    """Grace's optimization suggestions"""
    __tablename__ = "revenue_optimizations"
    
    id = Column(Integer, primary_key=True)
    optimization_id = Column(String(128), unique=True, nullable=False)
    
    # Suggestion
    suggestion_type = Column(String(64), nullable=False)  # increase_marketing, reduce_costs, etc
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    
    # Impact prediction
    expected_revenue_increase = Column(Float, default=0.0)
    expected_cost = Column(Float, default=0.0)
    expected_roi = Column(Float, default=0.0)
    confidence = Column(Float, default=0.5)
    
    # Reasoning
    reasoning = Column(Text, nullable=False)
    data_used = Column(JSON, default=list)
    
    # Status
    status = Column(String(32), default="pending")  # pending, approved, rejected, implemented
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    implemented_at = Column(DateTime(timezone=True), nullable=True)


class RevenueTracker:
    """Complete financial tracking and optimization system"""
    
    def __init__(self):
        self.temporal_reasoner = TemporalReasoner()
    
    async def track_income(
        self, 
        source: str, 
        amount: float, 
        category: str, 
        client_id: Optional[str] = None,
        description: Optional[str] = None,
        payment_method: Optional[str] = None,
        invoice_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record revenue transaction"""
        import uuid
        
        transaction_id = f"REV-{uuid.uuid4().hex[:12]}"
        
        async with async_session() as session:
            transaction = RevenueTransaction(
                transaction_id=transaction_id,
                amount=amount,
                source=source,
                category=category,
                client_id=client_id,
                description=description,
                payment_method=payment_method,
                invoice_id=invoice_id,
                status="completed"
            )
            session.add(transaction)
            await session.commit()
            
            # Update metrics
            await self._update_business_metrics(source, category)
            
            return {
                "transaction_id": transaction_id,
                "amount": amount,
                "source": source,
                "category": category,
                "status": "completed",
                "message": f"Revenue tracked: ${amount} from {source}"
            }
    
    async def track_expense(
        self, 
        category: str, 
        amount: float, 
        description: str,
        vendor: Optional[str] = None,
        receipt_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record expense"""
        import uuid
        
        expense_id = f"EXP-{uuid.uuid4().hex[:12]}"
        
        async with async_session() as session:
            expense = Expense(
                expense_id=expense_id,
                amount=amount,
                category=category,
                description=description,
                vendor=vendor,
                receipt_url=receipt_url,
                status="completed"
            )
            session.add(expense)
            await session.commit()
            
            return {
                "expense_id": expense_id,
                "amount": amount,
                "category": category,
                "status": "completed",
                "message": f"Expense tracked: ${amount} for {category}"
            }
    
    async def calculate_profit(
        self, 
        timeframe: str = "month",
        business: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate revenue - expenses for timeframe"""
        now = datetime.utcnow()
        
        if timeframe == "day":
            start_date = now - timedelta(days=1)
        elif timeframe == "week":
            start_date = now - timedelta(weeks=1)
        elif timeframe == "month":
            start_date = now - timedelta(days=30)
        elif timeframe == "quarter":
            start_date = now - timedelta(days=90)
        elif timeframe == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)
        
        async with async_session() as session:
            # Get revenue
            revenue_query = select(sql_func.sum(RevenueTransaction.amount)).where(
                RevenueTransaction.transaction_date >= start_date
            )
            if business:
                revenue_query = revenue_query.where(RevenueTransaction.source == business)
            
            revenue_result = await session.execute(revenue_query)
            total_revenue = revenue_result.scalar() or 0.0
            
            # Get expenses
            expense_query = select(sql_func.sum(Expense.amount)).where(
                Expense.expense_date >= start_date
            )
            expense_result = await session.execute(expense_query)
            total_expenses = expense_result.scalar() or 0.0
            
            profit = total_revenue - total_expenses
            margin = (profit / total_revenue * 100) if total_revenue > 0 else 0.0
            
            return {
                "timeframe": timeframe,
                "business": business or "all",
                "revenue": round(total_revenue, 2),
                "expenses": round(total_expenses, 2),
                "profit": round(profit, 2),
                "profit_margin": round(margin, 2)
            }
    
    async def forecast_revenue(self, months_ahead: int = 3) -> List[Dict[str, Any]]:
        """ML-based revenue forecasting using temporal reasoning"""
        await self.temporal_reasoner.initialize()
        
        # Get historical revenue data
        async with async_session() as session:
            result = await session.execute(
                select(RevenueTransaction)
                .order_by(RevenueTransaction.transaction_date.desc())
                .limit(365)
            )
            transactions = result.scalars().all()
        
        # Group by month
        monthly_revenue = defaultdict(float)
        for txn in transactions:
            month_key = txn.transaction_date.strftime("%Y-%m")
            monthly_revenue[month_key] += txn.amount
        
        # Simple forecasting (can be enhanced with real ML model)
        forecasts = []
        
        if len(monthly_revenue) >= 3:
            recent_months = sorted(monthly_revenue.items(), reverse=True)[:3]
            avg_revenue = statistics.mean([rev for _, rev in recent_months])
            
            # Calculate trend
            if len(monthly_revenue) >= 6:
                older_months = sorted(monthly_revenue.items(), reverse=True)[3:6]
                older_avg = statistics.mean([rev for _, rev in older_months])
                growth = (avg_revenue - older_avg) / older_avg if older_avg > 0 else 0
            else:
                growth = 0.05  # Default 5% growth
            
            # Generate forecasts
            now = datetime.utcnow()
            for i in range(1, months_ahead + 1):
                future_date = now + timedelta(days=30 * i)
                month_key = future_date.strftime("%Y-%m")
                
                predicted = avg_revenue * (1 + growth) ** i
                confidence = max(0.5, 0.9 - (i * 0.1))  # Decreases with distance
                
                import uuid
                forecast_id = f"FORECAST-{uuid.uuid4().hex[:12]}"
                
                async with async_session() as session:
                    forecast = RevenueForecast(
                        forecast_id=forecast_id,
                        predicted_amount=predicted,
                        timeframe=month_key,
                        confidence=confidence,
                        model_used="temporal_trend",
                        features_used=["historical_average", "growth_rate"],
                        forecast_for_date=future_date
                    )
                    session.add(forecast)
                    await session.commit()
                
                forecasts.append({
                    "month": month_key,
                    "predicted_revenue": round(predicted, 2),
                    "confidence": round(confidence, 2),
                    "model": "temporal_trend"
                })
        
        return forecasts
    
    async def analyze_revenue_sources(self) -> List[Dict[str, Any]]:
        """Analyze which businesses are performing best"""
        async with async_session() as session:
            # Last 90 days
            cutoff = datetime.utcnow() - timedelta(days=90)
            
            result = await session.execute(
                select(
                    RevenueTransaction.source,
                    RevenueTransaction.category,
                    sql_func.sum(RevenueTransaction.amount).label("total_revenue"),
                    sql_func.count(RevenueTransaction.id).label("transaction_count"),
                    sql_func.avg(RevenueTransaction.amount).label("avg_transaction")
                )
                .where(RevenueTransaction.transaction_date >= cutoff)
                .group_by(RevenueTransaction.source, RevenueTransaction.category)
                .order_by(sql_func.sum(RevenueTransaction.amount).desc())
            )
            
            sources = []
            for row in result:
                sources.append({
                    "source": row.source,
                    "category": row.category,
                    "total_revenue": round(row.total_revenue, 2),
                    "transaction_count": row.transaction_count,
                    "avg_transaction": round(row.avg_transaction, 2)
                })
            
            return sources
    
    async def calculate_growth_rate(self, timeframe: str = "month") -> Dict[str, Any]:
        """Calculate month-over-month or year-over-year growth"""
        now = datetime.utcnow()
        
        if timeframe == "month":
            current_start = now - timedelta(days=30)
            previous_start = now - timedelta(days=60)
            previous_end = now - timedelta(days=30)
        elif timeframe == "quarter":
            current_start = now - timedelta(days=90)
            previous_start = now - timedelta(days=180)
            previous_end = now - timedelta(days=90)
        else:  # year
            current_start = now - timedelta(days=365)
            previous_start = now - timedelta(days=730)
            previous_end = now - timedelta(days=365)
        
        async with async_session() as session:
            # Current period
            current_result = await session.execute(
                select(sql_func.sum(RevenueTransaction.amount))
                .where(RevenueTransaction.transaction_date >= current_start)
            )
            current_revenue = current_result.scalar() or 0.0
            
            # Previous period
            previous_result = await session.execute(
                select(sql_func.sum(RevenueTransaction.amount))
                .where(
                    RevenueTransaction.transaction_date >= previous_start,
                    RevenueTransaction.transaction_date < previous_end
                )
            )
            previous_revenue = previous_result.scalar() or 0.0
            
            if previous_revenue > 0:
                growth_rate = ((current_revenue - previous_revenue) / previous_revenue) * 100
            else:
                growth_rate = 0.0
            
            return {
                "timeframe": timeframe,
                "current_revenue": round(current_revenue, 2),
                "previous_revenue": round(previous_revenue, 2),
                "growth_rate": round(growth_rate, 2),
                "growth_direction": "up" if growth_rate > 0 else "down"
            }
    
    async def suggest_optimizations(self) -> List[Dict[str, Any]]:
        """Grace recommends revenue optimizations"""
        suggestions = []
        
        # Analyze current state
        sources = await self.analyze_revenue_sources()
        profit = await self.calculate_profit("month")
        growth = await self.calculate_growth_rate("month")
        
        import uuid
        
        # Suggestion 1: Focus on top performers
        if len(sources) > 0:
            top_source = sources[0]
            suggestion_id = f"OPT-{uuid.uuid4().hex[:12]}"
            
            expected_increase = top_source["total_revenue"] * 0.2  # 20% increase
            marketing_cost = expected_increase * 0.1  # 10% of increase
            roi = (expected_increase - marketing_cost) / marketing_cost if marketing_cost > 0 else 0
            
            async with async_session() as session:
                optimization = RevenueOptimization(
                    optimization_id=suggestion_id,
                    suggestion_type="increase_marketing",
                    title=f"Invest more in {top_source['source']}",
                    description=f"Your top revenue source is {top_source['source']} with ${top_source['total_revenue']}. Investing ${marketing_cost} in marketing could increase revenue by ${expected_increase}.",
                    expected_revenue_increase=expected_increase,
                    expected_cost=marketing_cost,
                    expected_roi=roi,
                    confidence=0.75,
                    reasoning=f"Based on historical data, {top_source['source']} has {top_source['transaction_count']} transactions averaging ${top_source['avg_transaction']}. Increasing visibility should drive more transactions.",
                    data_used=["revenue_sources", "transaction_patterns"],
                    status="pending"
                )
                session.add(optimization)
                await session.commit()
            
            suggestions.append({
                "id": suggestion_id,
                "type": "increase_marketing",
                "title": f"Invest more in {top_source['source']}",
                "expected_increase": round(expected_increase, 2),
                "cost": round(marketing_cost, 2),
                "roi": round(roi, 2),
                "confidence": 0.75
            })
        
        # Suggestion 2: Cost reduction if profit margin is low
        if profit["profit_margin"] < 20:
            suggestion_id = f"OPT-{uuid.uuid4().hex[:12]}"
            
            target_reduction = profit["expenses"] * 0.15  # 15% reduction
            
            async with async_session() as session:
                optimization = RevenueOptimization(
                    optimization_id=suggestion_id,
                    suggestion_type="reduce_costs",
                    title="Optimize operational expenses",
                    description=f"Current profit margin is {profit['profit_margin']}%. Reducing expenses by ${target_reduction} would improve margins significantly.",
                    expected_revenue_increase=0,
                    expected_cost=-target_reduction,
                    expected_roi=0,
                    confidence=0.65,
                    reasoning="Low profit margins indicate opportunity for cost optimization. Review recurring expenses and negotiate better rates.",
                    data_used=["profit_analysis", "expense_categories"],
                    status="pending"
                )
                session.add(optimization)
                await session.commit()
            
            suggestions.append({
                "id": suggestion_id,
                "type": "reduce_costs",
                "title": "Optimize operational expenses",
                "savings": round(target_reduction, 2),
                "confidence": 0.65
            })
        
        # Suggestion 3: Expand if growing well
        if growth["growth_rate"] > 15:
            suggestion_id = f"OPT-{uuid.uuid4().hex[:12]}"
            
            investment = growth["current_revenue"] * 0.3
            expected_return = investment * 1.5
            
            async with async_session() as session:
                optimization = RevenueOptimization(
                    optimization_id=suggestion_id,
                    suggestion_type="expand_services",
                    title="Expand to new service offerings",
                    description=f"You're growing at {growth['growth_rate']}% month-over-month. This is the perfect time to expand. Invest ${investment} to launch complementary services.",
                    expected_revenue_increase=expected_return,
                    expected_cost=investment,
                    expected_roi=(expected_return - investment) / investment,
                    confidence=0.70,
                    reasoning="Strong growth indicates market demand. Expanding services can capture more of this demand.",
                    data_used=["growth_rate", "market_conditions"],
                    status="pending"
                )
                session.add(optimization)
                await session.commit()
            
            suggestions.append({
                "id": suggestion_id,
                "type": "expand_services",
                "title": "Expand to new service offerings",
                "investment": round(investment, 2),
                "expected_return": round(expected_return, 2),
                "confidence": 0.70
            })
        
        return suggestions
    
    async def _update_business_metrics(self, business: str, category: str):
        """Update aggregated metrics for a business"""
        now = datetime.utcnow()
        period = now.strftime("%Y-%m")
        
        import uuid
        metric_id = f"METRIC-{business}-{period}"
        
        async with async_session() as session:
            # Check if metric exists
            result = await session.execute(
                select(BusinessMetrics).where(BusinessMetrics.metric_id == metric_id)
            )
            metric = result.scalar_one_or_none()
            
            # Calculate current metrics
            cutoff = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            revenue_result = await session.execute(
                select(
                    sql_func.sum(RevenueTransaction.amount),
                    sql_func.count(RevenueTransaction.id),
                    sql_func.count(sql_func.distinct(RevenueTransaction.client_id))
                )
                .where(
                    RevenueTransaction.source == business,
                    RevenueTransaction.transaction_date >= cutoff
                )
            )
            revenue_row = revenue_result.one()
            total_revenue = revenue_row[0] or 0.0
            txn_count = revenue_row[1] or 0
            client_count = revenue_row[2] or 0
            
            if metric:
                metric.revenue = total_revenue
                metric.transaction_count = txn_count
                metric.client_count = client_count
                metric.updated_at = now
            else:
                metric = BusinessMetrics(
                    metric_id=metric_id,
                    business_name=business,
                    category=category,
                    revenue=total_revenue,
                    expenses=0.0,
                    profit=total_revenue,
                    growth_rate=0.0,
                    transaction_count=txn_count,
                    client_count=client_count,
                    period=period
                )
                session.add(metric)
            
            await session.commit()


revenue_tracker = RevenueTracker()
