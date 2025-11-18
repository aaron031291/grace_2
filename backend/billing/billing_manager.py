"""
Billing Manager - Subscription and invoice management
"""

import secrets
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from .models import (
    Subscription, SubscriptionPlan, SubscriptionStatus,
    Invoice, InvoiceStatus, InvoiceLineItem,
    UsageRecord, UsageRecordType
)


class BillingManager:
    """Manage subscriptions, invoices, and usage"""
    
    PLAN_PRICING = {
        SubscriptionPlan.FREE: Decimal("0.00"),
        SubscriptionPlan.STARTER: Decimal("29.00"),
        SubscriptionPlan.PROFESSIONAL: Decimal("99.00"),
        SubscriptionPlan.ENTERPRISE: Decimal("499.00"),
    }
    
    PLAN_LIMITS = {
        SubscriptionPlan.FREE: {
            "api_calls_per_month": 1000,
            "storage_gb": 1,
            "bandwidth_gb": 10,
            "compute_hours": 10,
            "ai_tokens_per_month": 10000,
            "team_members": 1,
        },
        SubscriptionPlan.STARTER: {
            "api_calls_per_month": 50000,
            "storage_gb": 10,
            "bandwidth_gb": 100,
            "compute_hours": 100,
            "ai_tokens_per_month": 500000,
            "team_members": 5,
        },
        SubscriptionPlan.PROFESSIONAL: {
            "api_calls_per_month": 500000,
            "storage_gb": 100,
            "bandwidth_gb": 1000,
            "compute_hours": 1000,
            "ai_tokens_per_month": 5000000,
            "team_members": 25,
        },
        SubscriptionPlan.ENTERPRISE: {
            "api_calls_per_month": -1,  # unlimited
            "storage_gb": 1000,
            "bandwidth_gb": 10000,
            "compute_hours": 10000,
            "ai_tokens_per_month": -1,  # unlimited
            "team_members": -1,  # unlimited
        },
    }
    
    def __init__(self):
        self.subscriptions: Dict[str, Subscription] = {}
        self.invoices: Dict[str, Invoice] = {}
        self.usage_records: List[UsageRecord] = []
    
    def create_subscription(
        self,
        tenant_id: str,
        plan: SubscriptionPlan,
        billing_cycle: str = "monthly",
        trial_days: int = 14,
    ) -> Subscription:
        """Create a new subscription"""
        subscription_id = f"sub_{secrets.token_urlsafe(16)}"
        
        price_monthly = self.PLAN_PRICING[plan]
        price_yearly = price_monthly * 10  # 2 months free on yearly
        
        now = datetime.utcnow()
        trial_end = now + timedelta(days=trial_days) if trial_days > 0 else None
        
        subscription = Subscription(
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            plan=plan,
            status=SubscriptionStatus.TRIALING if trial_end else SubscriptionStatus.ACTIVE,
            price_monthly=price_monthly,
            price_yearly=price_yearly,
            billing_cycle=billing_cycle,
            trial_end=trial_end,
            current_period_start=now,
            current_period_end=now + timedelta(days=30 if billing_cycle == "monthly" else 365),
            limits=self.PLAN_LIMITS[plan].copy(),
        )
        
        self.subscriptions[subscription_id] = subscription
        return subscription
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID"""
        return self.subscriptions.get(subscription_id)
    
    def get_subscription_by_tenant(self, tenant_id: str) -> Optional[Subscription]:
        """Get subscription for tenant"""
        for sub in self.subscriptions.values():
            if sub.tenant_id == tenant_id:
                return sub
        return None
    
    def update_subscription(
        self,
        subscription_id: str,
        plan: Optional[SubscriptionPlan] = None,
        billing_cycle: Optional[str] = None,
    ) -> Subscription:
        """Update subscription"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription not found: {subscription_id}")
        
        if plan and plan != subscription.plan:
            subscription.plan = plan
            subscription.price_monthly = self.PLAN_PRICING[plan]
            subscription.price_yearly = subscription.price_monthly * 10
            subscription.limits = self.PLAN_LIMITS[plan].copy()
        
        if billing_cycle:
            subscription.billing_cycle = billing_cycle
        
        subscription.updated_at = datetime.utcnow()
        return subscription
    
    def cancel_subscription(self, subscription_id: str) -> Subscription:
        """Cancel subscription"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription not found: {subscription_id}")
        
        subscription.status = SubscriptionStatus.CANCELED
        subscription.canceled_at = datetime.utcnow()
        subscription.updated_at = datetime.utcnow()
        return subscription
    
    def create_invoice(
        self,
        tenant_id: str,
        subscription_id: Optional[str] = None,
        line_items: Optional[List[InvoiceLineItem]] = None,
    ) -> Invoice:
        """Create a new invoice"""
        invoice_id = f"inv_{secrets.token_urlsafe(16)}"
        invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        
        line_items = line_items or []
        subtotal = sum(item.amount for item in line_items)
        tax = subtotal * Decimal("0.10")  # 10% tax
        total = subtotal + tax
        
        invoice = Invoice(
            invoice_id=invoice_id,
            tenant_id=tenant_id,
            subscription_id=subscription_id,
            invoice_number=invoice_number,
            status=InvoiceStatus.OPEN,
            subtotal=subtotal,
            tax=tax,
            total=total,
            amount_due=total,
            line_items=line_items,
            due_date=datetime.utcnow() + timedelta(days=30),
        )
        
        self.invoices[invoice_id] = invoice
        return invoice
    
    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Get invoice by ID"""
        return self.invoices.get(invoice_id)
    
    def list_invoices(
        self,
        tenant_id: Optional[str] = None,
        status: Optional[InvoiceStatus] = None,
    ) -> List[Invoice]:
        """List invoices with optional filters"""
        invoices = list(self.invoices.values())
        
        if tenant_id:
            invoices = [i for i in invoices if i.tenant_id == tenant_id]
        if status:
            invoices = [i for i in invoices if i.status == status]
        
        return sorted(invoices, key=lambda i: i.invoice_date, reverse=True)
    
    def pay_invoice(self, invoice_id: str) -> Invoice:
        """Mark invoice as paid"""
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice not found: {invoice_id}")
        
        invoice.status = InvoiceStatus.PAID
        invoice.amount_paid = invoice.total
        invoice.amount_due = Decimal("0.00")
        invoice.paid_at = datetime.utcnow()
        invoice.updated_at = datetime.utcnow()
        return invoice
    
    def record_usage(
        self,
        tenant_id: str,
        usage_type: UsageRecordType,
        quantity: Decimal,
        unit: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UsageRecord:
        """Record usage"""
        record_id = f"usage_{secrets.token_urlsafe(16)}"
        
        subscription = self.get_subscription_by_tenant(tenant_id)
        
        record = UsageRecord(
            record_id=record_id,
            tenant_id=tenant_id,
            subscription_id=subscription.subscription_id if subscription else None,
            usage_type=usage_type,
            quantity=quantity,
            unit=unit,
            metadata=metadata or {},
        )
        
        self.usage_records.append(record)
        return record
    
    def get_usage_summary(
        self,
        tenant_id: str,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get usage summary for tenant"""
        if not period_start:
            period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not period_end:
            period_end = datetime.utcnow()
        
        records = [
            r for r in self.usage_records
            if r.tenant_id == tenant_id and period_start <= r.timestamp <= period_end
        ]
        
        summary = {}
        for usage_type in UsageRecordType:
            type_records = [r for r in records if r.usage_type == usage_type]
            if type_records:
                total_quantity = sum(r.quantity for r in type_records)
                summary[usage_type.value] = {
                    "quantity": float(total_quantity),
                    "unit": type_records[0].unit,
                    "records_count": len(type_records),
                }
        
        return {
            "tenant_id": tenant_id,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "usage": summary,
        }
