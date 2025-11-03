"""Tests for Payment and Marketplace Systems"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from backend.transcendence.business.payment_processor import payment_processor
from backend.transcendence.business.marketplace_connector import marketplace_connector
from backend.models import async_session
from backend.transcendence.business.models import (
    StripeTransaction,
    StripeWebhook,
    MarketplaceJob,
    MarketplaceProposal
)


@pytest.fixture
async def setup_database():
    """Setup test database"""
    from backend.models import Base, engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ========== PAYMENT PROCESSOR TESTS ==========

@pytest.mark.asyncio
async def test_create_invoice_mocked(setup_database):
    """Test invoice creation with mocked Stripe"""
    
    with patch('stripe.Invoice.create') as mock_create, \
         patch('stripe.InvoiceItem.create') as mock_item, \
         patch('stripe.Invoice.finalize_invoice') as mock_finalize:
        
        # Mock Stripe responses
        mock_create.return_value = Mock(id="inv_test123")
        mock_finalize.return_value = Mock(
            id="inv_test123",
            status="open",
            hosted_invoice_url="https://invoice.stripe.com/test",
            invoice_pdf="https://invoice.stripe.com/test.pdf",
            paid=False
        )
        
        # Mock Stripe initialization
        payment_processor._stripe_initialized = True
        
        # Create invoice
        result = await payment_processor.create_invoice(
            project_id=1,
            amount=500.0,
            description="Test project invoice",
            client_id="test_client_001"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["invoice_id"] == "inv_test123"
        assert result["amount"] == 500.0
        assert "signature" in result
        
        # Verify database
        async with async_session() as session:
            from sqlalchemy import select
            db_result = await session.execute(
                select(StripeTransaction).where(
                    StripeTransaction.stripe_invoice_id == "inv_test123"
                )
            )
            transaction = db_result.scalar_one_or_none()
            
            assert transaction is not None
            assert transaction.amount == 500.0
            assert transaction.status == "pending"
            assert transaction.project_id == 1


@pytest.mark.asyncio
async def test_process_payment_mocked(setup_database):
    """Test payment processing with mocked Stripe"""
    
    with patch('stripe.Invoice.retrieve') as mock_retrieve, \
         patch('stripe.Invoice.pay') as mock_pay:
        
        # Mock Stripe responses
        mock_retrieve.return_value = Mock(id="inv_test123")
        mock_pay.return_value = Mock(
            id="inv_test123",
            paid=True,
            status="paid",
            amount_paid=50000,  # cents
            payment_intent="pi_test123"
        )
        
        payment_processor._stripe_initialized = True
        
        # Create test transaction first
        async with async_session() as session:
            transaction = StripeTransaction(
                stripe_invoice_id="inv_test123",
                project_id=1,
                amount=500.0,
                status="pending",
                description="Test invoice"
            )
            session.add(transaction)
            await session.commit()
        
        # Process payment
        result = await payment_processor.process_payment(
            invoice_id="inv_test123"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["paid"] is True
        assert result["amount_paid"] == 500.0
        
        # Verify database update
        async with async_session() as session:
            from sqlalchemy import select
            db_result = await session.execute(
                select(StripeTransaction).where(
                    StripeTransaction.stripe_invoice_id == "inv_test123"
                )
            )
            transaction = db_result.scalar_one_or_none()
            
            assert transaction.status == "paid"
            assert transaction.stripe_payment_intent_id == "pi_test123"


@pytest.mark.asyncio
async def test_stripe_webhook_handling(setup_database):
    """Test Stripe webhook processing"""
    
    # Mock webhook payload
    payload = {
        "id": "evt_test123",
        "type": "invoice.paid",
        "data": {
            "object": {
                "id": "inv_test123",
                "amount_paid": 50000,
                "paid": True
            }
        }
    }
    
    # Create test transaction
    async with async_session() as session:
        transaction = StripeTransaction(
            stripe_invoice_id="inv_test123",
            project_id=1,
            amount=500.0,
            status="pending",
            description="Test invoice"
        )
        session.add(transaction)
        await session.commit()
    
    # Mock secrets vault to return None (skip signature verification for test)
    with patch('backend.secrets_vault.secrets_vault.retrieve_secret', 
               return_value=AsyncMock(return_value=None)):
        
        result = await payment_processor.handle_webhook(
            payload=payload,
            signature="test_signature"
        )
        
        # Should fail due to missing webhook secret
        assert result["success"] is False


@pytest.mark.asyncio
async def test_refund_payment(setup_database):
    """Test payment refund"""
    
    with patch('stripe.Refund.create') as mock_refund:
        
        # Mock Stripe response
        mock_refund.return_value = Mock(
            id="re_test123",
            status="succeeded",
            amount=50000
        )
        
        payment_processor._stripe_initialized = True
        
        # Create test transaction
        async with async_session() as session:
            transaction = StripeTransaction(
                stripe_invoice_id="inv_test123",
                stripe_payment_intent_id="pi_test123",
                project_id=1,
                amount=500.0,
                status="paid",
                description="Test invoice"
            )
            session.add(transaction)
            await session.commit()
        
        # Process refund
        result = await payment_processor.refund_payment(
            invoice_id="inv_test123",
            reason="Customer requested refund",
            approver="test_user"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["refund_id"] == "re_test123"
        assert result["amount"] == 500.0
        
        # Verify database update
        async with async_session() as session:
            from sqlalchemy import select
            db_result = await session.execute(
                select(StripeTransaction).where(
                    StripeTransaction.stripe_invoice_id == "inv_test123"
                )
            )
            transaction = db_result.scalar_one_or_none()
            
            assert transaction.refunded is True
            assert transaction.refund_amount == 500.0
            assert transaction.status == "refunded"


@pytest.mark.asyncio
async def test_track_payment_status(setup_database):
    """Test payment status tracking"""
    
    # Create test transaction
    async with async_session() as session:
        transaction = StripeTransaction(
            stripe_invoice_id="inv_test123",
            project_id=1,
            amount=500.0,
            status="paid",
            description="Test invoice"
        )
        session.add(transaction)
        await session.commit()
    
    # Get status
    result = await payment_processor.track_payment_status(
        invoice_id="inv_test123"
    )
    
    # Verify result
    assert result["success"] is True
    assert result["status"] == "paid"
    assert result["amount"] == 500.0


# ========== MARKETPLACE CONNECTOR TESTS ==========

@pytest.mark.asyncio
async def test_search_jobs(setup_database):
    """Test Upwork job search"""
    
    # Mock Upwork initialization
    marketplace_connector._upwork_client = "mock_client"
    
    # Search jobs
    jobs = await marketplace_connector.search_jobs(
        keywords="python developer",
        budget_min=500.0,
        limit=10
    )
    
    # Verify results
    assert isinstance(jobs, list)
    assert len(jobs) > 0
    
    # Verify database storage
    async with async_session() as session:
        from sqlalchemy import select
        db_result = await session.execute(
            select(MarketplaceJob).where(
                MarketplaceJob.platform == "upwork"
            )
        )
        db_jobs = db_result.scalars().all()
        
        assert len(db_jobs) > 0
        assert db_jobs[0].status == "discovered"


@pytest.mark.asyncio
async def test_submit_proposal_requires_approval(setup_database):
    """Test proposal submission requires governance approval"""
    
    # Create test job
    async with async_session() as session:
        job = MarketplaceJob(
            platform="upwork",
            job_id="upwork_test_job_001",
            title="Python Developer Needed",
            description="Build a web scraper",
            budget=800.0,
            status="discovered"
        )
        session.add(job)
        await session.commit()
    
    # Submit proposal without approval
    result = await marketplace_connector.submit_proposal(
        job_id="upwork_test_job_001",
        proposal_text="I can help with this project...",
        bid_amount=750.0,
        governance_approved=False
    )
    
    # Should require approval
    assert result["success"] is False
    assert result["requires_approval"] is True
    assert "proposal_id" in result


@pytest.mark.asyncio
async def test_submit_proposal_with_approval(setup_database):
    """Test proposal submission with governance approval"""
    
    marketplace_connector._upwork_client = "mock_client"
    
    # Create test job
    async with async_session() as session:
        job = MarketplaceJob(
            platform="upwork",
            job_id="upwork_test_job_002",
            title="Python Developer Needed",
            description="Build a web scraper",
            budget=800.0,
            status="discovered"
        )
        session.add(job)
        await session.commit()
    
    # Submit proposal with approval
    result = await marketplace_connector.submit_proposal(
        job_id="upwork_test_job_002",
        proposal_text="I can help with this project...",
        bid_amount=750.0,
        governance_approved=True
    )
    
    # Should succeed
    assert result["success"] is True
    assert "proposal_id" in result
    
    # Verify database
    async with async_session() as session:
        from sqlalchemy import select
        db_result = await session.execute(
            select(MarketplaceProposal).where(
                MarketplaceProposal.marketplace_job_id == "upwork_test_job_002"
            )
        )
        proposal = db_result.scalar_one_or_none()
        
        assert proposal is not None
        assert proposal.status == "submitted"
        assert proposal.governance_approved is True


@pytest.mark.asyncio
async def test_accept_contract(setup_database):
    """Test contract acceptance"""
    
    marketplace_connector._upwork_client = "mock_client"
    
    # Create test job
    async with async_session() as session:
        job = MarketplaceJob(
            platform="upwork",
            job_id="upwork_test_job_003",
            title="Python Developer Needed",
            description="Build a web scraper",
            budget=800.0,
            status="applied"
        )
        session.add(job)
        await session.commit()
    
    # Accept contract
    result = await marketplace_connector.accept_contract(
        job_id="upwork_test_job_003"
    )
    
    # Verify result
    assert result["success"] is True
    assert result["status"] == "in_progress"
    
    # Verify database
    async with async_session() as session:
        from sqlalchemy import select
        db_result = await session.execute(
            select(MarketplaceJob).where(
                MarketplaceJob.job_id == "upwork_test_job_003"
            )
        )
        job = db_result.scalar_one_or_none()
        
        assert job.status == "in_progress"


@pytest.mark.asyncio
async def test_submit_work(setup_database):
    """Test work submission"""
    
    marketplace_connector._upwork_client = "mock_client"
    
    # Create test job
    async with async_session() as session:
        job = MarketplaceJob(
            platform="upwork",
            job_id="upwork_test_job_004",
            title="Python Developer Needed",
            description="Build a web scraper",
            budget=800.0,
            status="in_progress"
        )
        session.add(job)
        await session.commit()
    
    # Submit work
    result = await marketplace_connector.submit_work(
        job_id="upwork_test_job_004",
        deliverables=["scraper.py", "README.md"],
        description="Completed web scraper with documentation"
    )
    
    # Verify result
    assert result["success"] is True
    assert "deliverable_id" in result
    
    # Verify job status updated
    async with async_session() as session:
        from sqlalchemy import select
        db_result = await session.execute(
            select(MarketplaceJob).where(
                MarketplaceJob.job_id == "upwork_test_job_004"
            )
        )
        job = db_result.scalar_one_or_none()
        
        assert job.status == "completed"


@pytest.mark.asyncio
async def test_request_payment(setup_database):
    """Test payment request"""
    
    marketplace_connector._upwork_client = "mock_client"
    
    # Create test job
    async with async_session() as session:
        job = MarketplaceJob(
            platform="upwork",
            job_id="upwork_test_job_005",
            title="Python Developer Needed",
            description="Build a web scraper",
            budget=800.0,
            status="completed"
        )
        session.add(job)
        await session.commit()
    
    # Request payment
    result = await marketplace_connector.request_payment(
        job_id="upwork_test_job_005"
    )
    
    # Verify result
    assert result["success"] is True
    assert result["amount"] == 800.0
    assert result["status"] == "paid"


# ========== END-TO-END TEST ==========

@pytest.mark.asyncio
async def test_end_to_end_workflow(setup_database):
    """
    End-to-end test: Find job → Apply → Win → Deliver → Get paid
    """
    
    marketplace_connector._upwork_client = "mock_client"
    
    # 1. Search for jobs
    jobs = await marketplace_connector.search_jobs(
        keywords="python developer",
        budget_min=500.0,
        limit=5
    )
    
    assert len(jobs) > 0
    test_job_id = jobs[0]["id"]
    
    # 2. Submit proposal (with approval)
    proposal_result = await marketplace_connector.submit_proposal(
        job_id=test_job_id,
        proposal_text="I am experienced in Python development...",
        bid_amount=750.0,
        governance_approved=True
    )
    
    assert proposal_result["success"] is True
    
    # 3. Accept contract (simulate winning the job)
    accept_result = await marketplace_connector.accept_contract(
        job_id=test_job_id
    )
    
    assert accept_result["success"] is True
    assert accept_result["status"] == "in_progress"
    
    # 4. Submit work
    submit_result = await marketplace_connector.submit_work(
        job_id=test_job_id,
        deliverables=["deliverable1.py", "deliverable2.py"],
        description="Completed project deliverables"
    )
    
    assert submit_result["success"] is True
    
    # 5. Request payment
    payment_result = await marketplace_connector.request_payment(
        job_id=test_job_id
    )
    
    assert payment_result["success"] is True
    assert payment_result["status"] == "paid"
    
    # Verify final job status
    async with async_session() as session:
        from sqlalchemy import select
        db_result = await session.execute(
            select(MarketplaceJob).where(
                MarketplaceJob.job_id == test_job_id
            )
        )
        job = db_result.scalar_one_or_none()
        
        assert job.status == "paid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
