"""Business Database Models"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from backend.models.base_models import Base


class StripeTransaction(Base):
    """Stripe payment transaction record"""
    __tablename__ = "stripe_transactions"
    
    id = Column(Integer, primary_key=True)
    
    # Stripe IDs
    stripe_invoice_id = Column(String(128), unique=True, nullable=False)
    stripe_payment_intent_id = Column(String(128), nullable=True)
    stripe_customer_id = Column(String(128), nullable=True)
    stripe_subscription_id = Column(String(128), nullable=True)
    
    # Transaction details
    project_id = Column(Integer, nullable=True)
    client_id = Column(String(128), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="usd")
    description = Column(Text, nullable=True)
    
    # Status
    status = Column(String(32), nullable=False)  # pending, paid, failed, refunded
    payment_method = Column(String(64), nullable=True)
    
    # Refunds
    refunded = Column(Boolean, default=False)
    refund_amount = Column(Float, nullable=True)
    refund_reason = Column(Text, nullable=True)
    refund_approved_by = Column(String(64), nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Governance
    governance_approval_id = Column(Integer, nullable=True)
    parliament_approval_id = Column(Integer, nullable=True)
    verification_signature = Column(String(256), nullable=True)
    
    # Metadata
    transaction_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StripeWebhook(Base):
    """Stripe webhook event log"""
    __tablename__ = "stripe_webhooks"
    
    id = Column(Integer, primary_key=True)
    
    # Webhook details
    stripe_event_id = Column(String(128), unique=True, nullable=False)
    event_type = Column(String(64), nullable=False)
    
    # Payload
    payload = Column(JSON, nullable=False)
    
    # Processing
    processed = Column(Boolean, default=False)
    processing_result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Security
    signature_valid = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)


class PaymentMethod(Base):
    """Stored payment methods for clients"""
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True)
    
    # Client
    client_id = Column(String(128), nullable=False)
    stripe_customer_id = Column(String(128), nullable=False)
    stripe_payment_method_id = Column(String(128), nullable=False)
    
    # Details
    payment_type = Column(String(32), nullable=False)  # card, bank_account, etc.
    last_four = Column(String(4), nullable=True)
    brand = Column(String(32), nullable=True)
    
    # Status
    default = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MarketplaceJob(Base):
    """Jobs from Upwork/Fiverr"""
    __tablename__ = "marketplace_jobs"
    
    id = Column(Integer, primary_key=True)
    
    # Marketplace
    platform = Column(String(32), nullable=False)  # upwork, fiverr
    job_id = Column(String(128), unique=True, nullable=False)
    
    # Job details
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    budget = Column(Float, nullable=True)
    budget_type = Column(String(32), nullable=True)  # fixed, hourly
    
    # Client
    client_id = Column(String(128), nullable=True)
    client_name = Column(String(128), nullable=True)
    client_rating = Column(Float, nullable=True)
    
    # Status
    status = Column(String(32), default="discovered")  # discovered, analyzed, applied, won, in_progress, completed, paid
    hunter_score = Column(Float, nullable=True)
    grace_recommendation = Column(Text, nullable=True)
    
    # Metadata
    skills_required = Column(JSON, nullable=True)
    job_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MarketplaceProposal(Base):
    """Proposals submitted to marketplace jobs"""
    __tablename__ = "marketplace_proposals"
    
    id = Column(Integer, primary_key=True)
    
    # Job reference
    job_id = Column(Integer, ForeignKey("marketplace_jobs.id"), nullable=False)
    marketplace_job_id = Column(String(128), nullable=False)
    platform = Column(String(32), nullable=False)
    
    # Proposal
    proposal_text = Column(Text, nullable=False)
    bid_amount = Column(Float, nullable=True)
    estimated_hours = Column(Integer, nullable=True)
    
    # Approval
    governance_approved = Column(Boolean, default=False)
    parliament_approved = Column(Boolean, default=False)
    approved_by = Column(String(64), nullable=True)
    approval_id = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(32), default="draft")  # draft, submitted, accepted, rejected
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Response
    client_response = Column(Text, nullable=True)
    acceptance_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MarketplaceMessage(Base):
    """Messages exchanged with marketplace clients"""
    __tablename__ = "marketplace_messages"
    
    id = Column(Integer, primary_key=True)
    
    # Job/Contract
    job_id = Column(Integer, ForeignKey("marketplace_jobs.id"), nullable=True)
    marketplace_job_id = Column(String(128), nullable=True)
    platform = Column(String(32), nullable=False)
    client_id = Column(String(128), nullable=False)
    
    # Message
    direction = Column(String(16), nullable=False)  # inbound, outbound
    message_text = Column(Text, nullable=False)
    
    # Auto-response
    auto_generated = Column(Boolean, default=False)
    grace_approved = Column(Boolean, default=False)
    human_reviewed = Column(Boolean, default=False)
    
    # Thread
    thread_id = Column(String(128), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MarketplaceDeliverable(Base):
    """Deliverables for marketplace jobs"""
    __tablename__ = "marketplace_deliverables"
    
    id = Column(Integer, primary_key=True)
    
    # Job
    job_id = Column(Integer, ForeignKey("marketplace_jobs.id"), nullable=False)
    marketplace_job_id = Column(String(128), nullable=False)
    platform = Column(String(32), nullable=False)
    
    # Deliverable
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    file_paths = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(32), default="draft")  # draft, submitted, accepted, revision_requested
    
    # Submission
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Feedback
    client_feedback = Column(Text, nullable=True)
    revision_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
