"""
Billing Models
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from decimal import Decimal


class SubscriptionPlan(str, Enum):
    """Subscription plans"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"


class Subscription(BaseModel):
    """Subscription model"""
    subscription_id: str
    tenant_id: str
    
    plan: SubscriptionPlan
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    
    price_monthly: Decimal = Decimal("0.00")
    price_yearly: Decimal = Decimal("0.00")
    billing_cycle: str = "monthly"  # "monthly" or "yearly"
    
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    stripe_payment_method_id: Optional[str] = None
    
    trial_end: Optional[datetime] = None
    current_period_start: datetime = Field(default_factory=datetime.utcnow)
    current_period_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    
    limits: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InvoiceStatus(str, Enum):
    """Invoice status"""
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class InvoiceLineItem(BaseModel):
    """Invoice line item"""
    description: str
    quantity: int = 1
    unit_price: Decimal
    amount: Decimal
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Invoice(BaseModel):
    """Invoice model"""
    invoice_id: str
    tenant_id: str
    subscription_id: Optional[str] = None
    
    invoice_number: str
    status: InvoiceStatus = InvoiceStatus.DRAFT
    
    subtotal: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")
    amount_paid: Decimal = Decimal("0.00")
    amount_due: Decimal = Decimal("0.00")
    
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    
    stripe_invoice_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    
    invoice_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    
    invoice_pdf_url: Optional[str] = None
    hosted_invoice_url: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UsageRecordType(str, Enum):
    """Usage record types"""
    API_CALLS = "api_calls"
    STORAGE_GB = "storage_gb"
    BANDWIDTH_GB = "bandwidth_gb"
    COMPUTE_HOURS = "compute_hours"
    AI_TOKENS = "ai_tokens"


class UsageRecord(BaseModel):
    """Usage tracking record"""
    record_id: str
    tenant_id: str
    subscription_id: Optional[str] = None
    
    usage_type: UsageRecordType
    quantity: Decimal
    unit: str  # "calls", "GB", "hours", "tokens", etc.
    
    unit_price: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    
    # Metadata
    resource_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    period_start: datetime = Field(default_factory=datetime.utcnow)
    period_end: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
