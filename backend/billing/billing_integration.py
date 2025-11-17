"""
Billing Integration Framework
Stripe integration for subscriptions, usage tracking, and invoicing
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid

class BillingCycle(str, Enum):
    """Billing cycle"""
    MONTHLY = "monthly"
    ANNUAL = "annual"

class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    TRIAL = "trial"

@dataclass
class Subscription:
    """Customer subscription"""
    subscription_id: str
    tenant_id: str
    plan_id: str
    status: SubscriptionStatus
    billing_cycle: BillingCycle
    amount_cents: int
    currency: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    stripe_subscription_id: Optional[str] = None

@dataclass
class UsageRecord:
    """Usage tracking for metered billing"""
    record_id: str
    tenant_id: str
    metric_name: str
    quantity: int
    timestamp: datetime
    billing_period: str

@dataclass
class Invoice:
    """Invoice"""
    invoice_id: str
    tenant_id: str
    amount_cents: int
    currency: str
    status: str
    due_date: datetime
    line_items: List[Dict[str, Any]]
    stripe_invoice_id: Optional[str] = None

class BillingManager:
    """Manages billing and subscriptions"""
    
    def __init__(self, stripe_api_key: Optional[str] = None):
        self.stripe_api_key = stripe_api_key
        self.subscriptions: Dict[str, Subscription] = {}
        self.usage_records: List[UsageRecord] = []
        self.invoices: Dict[str, Invoice] = {}
        
        # Plan definitions
        self.plans = {
            "free": {"price_cents": 0, "name": "Free Tier"},
            "starter": {"price_cents": 2900, "name": "Starter", "currency": "usd"},
            "pro": {"price_cents": 9900, "name": "Pro", "currency": "usd"},
            "enterprise": {"price_cents": 49900, "name": "Enterprise", "currency": "usd"}
        }
    
    def create_subscription(
        self,
        tenant_id: str,
        plan_id: str,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY
    ) -> Subscription:
        """Create a new subscription"""
        subscription_id = f"sub_{uuid.uuid4().hex[:12]}"
        
        plan = self.plans.get(plan_id)
        if not plan:
            raise ValueError(f"Unknown plan: {plan_id}")
        
        now = datetime.now()
        
        subscription = Subscription(
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            plan_id=plan_id,
            status=SubscriptionStatus.TRIAL if plan_id == "free" else SubscriptionStatus.ACTIVE,
            billing_cycle=billing_cycle,
            amount_cents=plan["price_cents"],
            currency=plan.get("currency", "usd"),
            current_period_start=now,
            current_period_end=now,  # Would calculate based on cycle
            cancel_at_period_end=False
        )
        
        self.subscriptions[subscription_id] = subscription
        return subscription
    
    def record_usage(
        self,
        tenant_id: str,
        metric_name: str,
        quantity: int
    ) -> UsageRecord:
        """Record usage for metered billing"""
        record_id = f"usage_{uuid.uuid4().hex[:12]}"
        
        record = UsageRecord(
            record_id=record_id,
            tenant_id=tenant_id,
            metric_name=metric_name,
            quantity=quantity,
            timestamp=datetime.now(),
            billing_period=datetime.now().strftime("%Y-%m")
        )
        
        self.usage_records.append(record)
        return record
    
    def generate_invoice(
        self,
        tenant_id: str,
        subscription_id: str
    ) -> Invoice:
        """Generate invoice for tenant"""
        invoice_id = f"inv_{uuid.uuid4().hex[:12]}"
        
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription not found: {subscription_id}")
        
        # Calculate usage charges
        period = datetime.now().strftime("%Y-%m")
        period_usage = [
            u for u in self.usage_records
            if u.tenant_id == tenant_id and u.billing_period == period
        ]
        
        line_items = [
            {
                "description": f"Subscription - {subscription.plan_id}",
                "amount_cents": subscription.amount_cents,
                "quantity": 1
            }
        ]
        
        # Add usage charges
        usage_by_metric = {}
        for usage in period_usage:
            usage_by_metric[usage.metric_name] = usage_by_metric.get(usage.metric_name, 0) + usage.quantity
        
        for metric, qty in usage_by_metric.items():
            line_items.append({
                "description": f"Usage - {metric}",
                "amount_cents": qty * 10,  # $0.10 per unit
                "quantity": qty
            })
        
        total_amount = sum(item["amount_cents"] for item in line_items)
        
        invoice = Invoice(
            invoice_id=invoice_id,
            tenant_id=tenant_id,
            amount_cents=total_amount,
            currency="usd",
            status="open",
            due_date=datetime.now(),  # Would calculate due date
            line_items=line_items
        )
        
        self.invoices[invoice_id] = invoice
        return invoice
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID"""
        return self.subscriptions.get(subscription_id)
    
    def cancel_subscription(self, subscription_id: str, immediate: bool = False):
        """Cancel subscription"""
        subscription = self.subscriptions.get(subscription_id)
        if subscription:
            if immediate:
                subscription.status = SubscriptionStatus.CANCELLED
            else:
                subscription.cancel_at_period_end = True

# Global instance
_billing_manager: Optional[BillingManager] = None

def get_billing_manager() -> BillingManager:
    """Get global billing manager"""
    global _billing_manager
    if _billing_manager is None:
        _billing_manager = BillingManager()
    return _billing_manager
