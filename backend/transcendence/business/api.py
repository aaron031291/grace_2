"""Business API Routes for Revenue Tracking"""

from fastapi import APIRouter, Depends
from typing import Optional
from ...auth import get_current_user
from .revenue_tracker import revenue_tracker

router = APIRouter(prefix="/api/business", tags=["business"])


@router.post("/revenue/track")
async def track_revenue(
    source: str,
    amount: float,
    category: str,
    client_id: Optional[str] = None,
    description: Optional[str] = None,
    payment_method: Optional[str] = None,
    invoice_id: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Track revenue transaction"""
    return await revenue_tracker.track_income(
        source=source,
        amount=amount,
        category=category,
        client_id=client_id,
        description=description,
        payment_method=payment_method,
        invoice_id=invoice_id
    )


@router.post("/revenue/expense")
async def track_expense(
    category: str,
    amount: float,
    description: str,
    vendor: Optional[str] = None,
    receipt_url: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Track expense"""
    return await revenue_tracker.track_expense(
        category=category,
        amount=amount,
        description=description,
        vendor=vendor,
        receipt_url=receipt_url
    )


@router.get("/revenue/profit")
async def get_profit(
    timeframe: str = "month",
    business: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Get profit calculation"""
    return await revenue_tracker.calculate_profit(timeframe, business)


@router.get("/revenue/sources")
async def get_revenue_sources(current_user: str = Depends(get_current_user)):
    """Get revenue source analysis"""
    sources = await revenue_tracker.analyze_revenue_sources()
    return {"sources": sources, "count": len(sources)}


@router.get("/revenue/growth")
async def get_growth_rate(
    timeframe: str = "month",
    current_user: str = Depends(get_current_user)
):
    """Get growth rate"""
    return await revenue_tracker.calculate_growth_rate(timeframe)


@router.get("/revenue/forecast")
async def get_forecast(
    months: int = 3,
    current_user: str = Depends(get_current_user)
):
    """Get revenue forecast"""
    forecasts = await revenue_tracker.forecast_revenue(months)
    return {"forecasts": forecasts}


@router.get("/revenue/optimizations")
async def get_optimizations(current_user: str = Depends(get_current_user)):
    """Get optimization suggestions"""
    suggestions = await revenue_tracker.suggest_optimizations()
    return {"suggestions": suggestions, "count": len(suggestions)}
