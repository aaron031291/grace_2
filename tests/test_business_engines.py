"""Tests for Business Automation Engines"""

import pytest
from datetime import datetime
from sqlalchemy import select

from backend.models import async_session
from backend.transcendence.business.models import Client, Lead, Project, Invoice
from backend.transcendence.business.ai_consulting_engine import AIConsultingEngine
from backend.transcendence.business.client_pipeline import ClientPipeline


@pytest.fixture
async def consulting_engine():
    engine = AIConsultingEngine()
    await engine.initialize()
    return engine


@pytest.fixture
async def client_pipeline():
    return ClientPipeline()


@pytest.mark.asyncio
async def test_lead_qualification(consulting_engine):
    """Test ML-based lead qualification"""
    client_data = {
        "email": "test@example.com",
        "company": "Test Corp",
        "industry": "technology",
        "budget": 15000,
        "budget_range": "$10k-$20k",
        "source": "referral",
        "requirements": "Need complete AI consulting for ML pipeline and deployment"
    }
    
    result = await consulting_engine.qualify_lead(client_data)
    
    assert "score" in result
    assert 0 <= result["score"] <= 100
    assert "qualified" in result
    assert "recommendation" in result
    assert "features" in result
    
    assert result["score"] > 70
    assert result["qualified"] is True


@pytest.mark.asyncio
async def test_lead_qualification_low_score(consulting_engine):
    """Test lead disqualification for low-quality leads"""
    client_data = {
        "email": "lowquality@example.com",
        "source": "cold",
        "requirements": "maybe something"
    }
    
    result = await consulting_engine.qualify_lead(client_data)
    
    assert result["score"] < 70
    assert result["qualified"] is False


@pytest.mark.asyncio
async def test_proposal_generation(consulting_engine):
    """Test automated proposal generation"""
    async with async_session() as session:
        client = Client(
            name="Test Client",
            email="client@test.com",
            company="Test Inc",
            industry="finance",
            source="referral"
        )
        session.add(client)
        await session.commit()
        await session.refresh(client)
        
        requirements = "Build ML-based fraud detection system with real-time monitoring"
        budget = 20000
        
        proposal = await consulting_engine.generate_proposal(
            requirements=requirements,
            client_id=client.id,
            budget=budget
        )
        
        assert "proposal_text" in proposal
        assert "deliverables" in proposal
        assert "timeline" in proposal
        assert "pricing" in proposal
        
        assert len(proposal["deliverables"]) > 0
        assert proposal["pricing"]["final_price"] <= budget
        assert proposal["auto_generated"] is True


@pytest.mark.asyncio
async def test_project_plan_creation(consulting_engine):
    """Test project plan breakdown"""
    async with async_session() as session:
        client = Client(
            name="Plan Test Client",
            email="plan@test.com",
            source="upwork"
        )
        session.add(client)
        await session.commit()
        await session.refresh(client)
        
        proposal = {
            "deliverables": [
                {"id": 1, "description": "Phase 1", "estimated_hours": 40},
                {"id": 2, "description": "Phase 2", "estimated_hours": 60}
            ],
            "timeline": {
                "total_hours": 100,
                "estimated_weeks": 3
            },
            "pricing": {
                "final_price": 15000
            }
        }
        
        plan = await consulting_engine.create_project_plan(
            proposal=proposal,
            client_id=client.id
        )
        
        assert "project_id" in plan
        assert "milestones" in plan
        assert len(plan["milestones"]) == 2
        
        result = await session.execute(
            select(Project).where(Project.id == plan["project_id"])
        )
        project = result.scalar_one()
        
        assert project.client_id == client.id
        assert project.status == "planned"
        assert project.proposal_generated is True


@pytest.mark.asyncio
async def test_pipeline_lead_capture(client_pipeline):
    """Test lead capture from various sources"""
    lead_data = {
        "name": "Pipeline Test",
        "email": "pipeline@test.com",
        "company": "Pipeline Corp",
        "budget": 10000,
        "requirements": "AI consulting needed",
        "project_type": "ML Pipeline"
    }
    
    result = await client_pipeline.capture_lead(
        source="upwork",
        data=lead_data
    )
    
    assert "client_id" in result
    assert "lead_id" in result
    assert result["stage"] == "LEAD"
    
    async with async_session() as session:
        client_result = await session.execute(
            select(Client).where(Client.id == result["client_id"])
        )
        client = client_result.scalar_one()
        assert client.email == "pipeline@test.com"
        assert client.source == "upwork"
        
        lead_result = await session.execute(
            select(Lead).where(Lead.id == result["lead_id"])
        )
        lead = lead_result.scalar_one()
        assert lead.stage == "LEAD"
        assert lead.score == 0.0


@pytest.mark.asyncio
async def test_pipeline_qualification(client_pipeline):
    """Test pipeline lead qualification"""
    lead_data = {
        "name": "Qualified Test",
        "email": "qualified@test.com",
        "company": "Big Company",
        "industry": "technology",
        "budget": 25000,
        "requirements": "Complete ML platform build with training and deployment",
        "timeline": "3 months"
    }
    
    capture_result = await client_pipeline.capture_lead(
        source="referral",
        data=lead_data
    )
    
    qual_result = await client_pipeline.qualify_lead(capture_result["lead_id"])
    
    assert qual_result["qualified"] is True
    assert qual_result["score"] >= 70
    assert qual_result["stage"] == "QUALIFIED"


@pytest.mark.asyncio
async def test_pipeline_stage_progression(client_pipeline):
    """Test moving through pipeline stages"""
    lead_data = {
        "name": "Stage Test",
        "email": "stages@test.com",
        "budget": 5000
    }
    
    capture = await client_pipeline.capture_lead("website", lead_data)
    lead_id = capture["lead_id"]
    
    stages = ["QUALIFIED", "PROPOSAL", "NEGOTIATION", "CONTRACT", "ACTIVE"]
    
    for stage in stages:
        result = await client_pipeline.move_to_stage(lead_id, stage)
        assert result["new_stage"] == stage
        assert "next_action" in result


@pytest.mark.asyncio
async def test_pipeline_metrics(client_pipeline):
    """Test pipeline metrics calculation"""
    for i in range(5):
        await client_pipeline.capture_lead(
            "upwork",
            {
                "name": f"Metrics Test {i}",
                "email": f"metrics{i}@test.com",
                "budget": 5000
            }
        )
    
    metrics = await client_pipeline.get_pipeline_metrics()
    
    assert "total_leads" in metrics
    assert "conversion_rate" in metrics
    assert "stage_counts" in metrics
    assert "funnel_conversion" in metrics
    assert "pipeline_value" in metrics
    
    assert metrics["total_leads"] >= 5


@pytest.mark.asyncio
async def test_close_rate_prediction(client_pipeline):
    """Test ML close rate prediction"""
    lead_data = {
        "name": "Prediction Test",
        "email": "predict@test.com",
        "company": "Test Co",
        "industry": "technology",
        "budget": 15000,
        "requirements": "ML consulting"
    }
    
    capture = await client_pipeline.capture_lead("referral", lead_data)
    await client_pipeline.qualify_lead(capture["lead_id"])
    await client_pipeline.move_to_stage(capture["lead_id"], "PROPOSAL")
    
    prediction = await client_pipeline.predict_close_rate(capture["lead_id"])
    
    assert "close_probability" in prediction
    assert 0 <= prediction["close_probability"] <= 1
    assert "confidence" in prediction
    assert "estimated_days_to_close" in prediction
    assert "factors" in prediction


@pytest.mark.asyncio
async def test_next_action_suggestion(client_pipeline):
    """Test Grace's next action recommendations"""
    lead_data = {
        "name": "Action Test",
        "email": "action@test.com",
        "budget": 8000
    }
    
    capture = await client_pipeline.capture_lead("website", lead_data)
    
    suggestion = await client_pipeline.suggest_next_action(capture["lead_id"])
    
    assert "current_stage" in suggestion
    assert "suggestion" in suggestion
    assert "can_automate" in suggestion
    assert "needs_approval" in suggestion
    
    assert suggestion["current_stage"] == "LEAD"
    assert "qualify" in suggestion["suggestion"]["action"].lower()


@pytest.mark.asyncio
async def test_payment_collection(consulting_engine):
    """Test invoice generation and payment tracking"""
    async with async_session() as session:
        client = Client(
            name="Payment Test",
            email="payment@test.com",
            source="upwork"
        )
        session.add(client)
        await session.flush()
        
        project = Project(
            client_id=client.id,
            title="Payment Test Project",
            scope="Test project",
            budget=10000,
            status="completed"
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        payment_result = await consulting_engine.collect_payment(
            project_id=project.id,
            payment_method="stripe"
        )
        
        assert "invoice_id" in payment_result
        assert "invoice_number" in payment_result
        assert payment_result["amount"] == 10000
        assert payment_result["status"] == "issued"
        
        invoice_result = await session.execute(
            select(Invoice).where(Invoice.id == payment_result["invoice_id"])
        )
        invoice = invoice_result.scalar_one()
        
        assert invoice.project_id == project.id
        assert invoice.amount == 10000
        assert invoice.status == "issued"


@pytest.mark.asyncio
async def test_satisfaction_tracking(consulting_engine):
    """Test NPS scoring"""
    async with async_session() as session:
        client = Client(
            name="NPS Test",
            email="nps@test.com",
            source="referral"
        )
        session.add(client)
        await session.flush()
        
        project = Project(
            client_id=client.id,
            title="NPS Test Project",
            scope="Test",
            budget=5000,
            status="completed"
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        nps_result = await consulting_engine.track_client_satisfaction(project.id)
        
        assert "nps_score" in nps_result
        assert 0 <= nps_result["nps_score"] <= 10
        assert "category" in nps_result
        assert nps_result["category"] in ["Promoter", "Passive", "Detractor"]


@pytest.mark.asyncio
async def test_end_to_end_lead_to_paid(client_pipeline, consulting_engine):
    """End-to-end test: Lead → Qualified → Proposal → Project → Paid"""
    lead_data = {
        "name": "E2E Test Client",
        "email": "e2e@test.com",
        "company": "E2E Corp",
        "industry": "technology",
        "budget": 20000,
        "requirements": "Full ML consulting engagement with deployment",
        "timeline": "2 months"
    }
    
    capture = await client_pipeline.capture_lead("referral", lead_data)
    assert capture["stage"] == "LEAD"
    
    qual = await client_pipeline.qualify_lead(capture["lead_id"])
    assert qual["qualified"] is True
    
    await client_pipeline.move_to_stage(capture["lead_id"], "PROPOSAL")
    
    proposal = await consulting_engine.generate_proposal(
        requirements=lead_data["requirements"],
        client_id=capture["client_id"],
        budget=lead_data["budget"]
    )
    assert proposal["auto_generated"] is True
    
    plan = await consulting_engine.create_project_plan(
        proposal=proposal,
        client_id=capture["client_id"]
    )
    assert "project_id" in plan
    
    await client_pipeline.move_to_stage(capture["lead_id"], "ACTIVE")
    await client_pipeline.move_to_stage(capture["lead_id"], "DELIVERED")
    
    payment = await consulting_engine.collect_payment(
        project_id=plan["project_id"]
    )
    assert payment["status"] == "issued"
    
    await client_pipeline.move_to_stage(capture["lead_id"], "PAID")
    
    nps = await consulting_engine.track_client_satisfaction(plan["project_id"])
    assert "nps_score" in nps
    
    metrics = await client_pipeline.get_pipeline_metrics()
    assert metrics["total_leads"] >= 1
    assert metrics["converted"] >= 1
