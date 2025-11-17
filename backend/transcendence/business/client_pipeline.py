"""Client Pipeline - CRM and Sales Funnel Management"""

from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, update, func

from ...models import async_session
from ...governance import governance_engine
from ...immutable_log import ImmutableLog
from ...websocket_manager import WebSocketManager
from .models import Client, Lead, Project, Interaction
from .ai_consulting_engine import AIConsultingEngine


class ClientPipeline:
    """Complete CRM and sales funnel with ML automation"""
    
    STAGES = [
        "LEAD",
        "QUALIFIED",
        "PROPOSAL",
        "NEGOTIATION",
        "CONTRACT",
        "ACTIVE",
        "DELIVERED",
        "PAID",
        "REPEAT"
    ]
    
    LOST_STAGES = ["LOST", "DISQUALIFIED", "GHOSTED"]
    
    def __init__(self):
        self.audit = ImmutableLog()
        self.ws_manager = WebSocketManager()
        self.consulting_engine = AIConsultingEngine()
        
    async def capture_lead(
        self,
        source: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Capture new lead from Upwork, website, referrals
        """
        await governance_engine.check_policy(
            action="capture_lead",
            context={"source": source}
        )
        
        async with async_session() as session:
            client = Client(
                name=data.get("name", "Unknown"),
                email=data["email"],
                company=data.get("company"),
                industry=data.get("industry"),
                budget_range=data.get("budget_range"),
                source=source,
                country=data.get("country"),
                timezone=data.get("timezone"),
                notes=data.get("notes")
            )
            session.add(client)
            await session.flush()
            
            lead = Lead(
                client_id=client.id,
                stage="LEAD",
                score=0.0,
                probability=0.0,
                project_type=data.get("project_type"),
                requirements=data.get("requirements"),
                timeline=data.get("timeline"),
                budget=data.get("budget"),
                qualification_data=data,
                next_action="Qualify lead",
                next_action_date=datetime.utcnow() + timedelta(hours=24)
            )
            session.add(lead)
            
            interaction = Interaction(
                client_id=client.id,
                interaction_type="inbound",
                channel=source,
                content=f"New lead captured from {source}",
                automated=True,
                grace_generated=True
            )
            session.add(interaction)
            
            await session.commit()
            await session.refresh(client)
            await session.refresh(lead)
            
            await self.audit.log(
                action="lead_captured",
                user="client_pipeline",
                details={
                    "client_id": client.id,
                    "lead_id": lead.id,
                    "source": source
                }
            )
            
            await self.ws_manager.broadcast({
                "type": "lead_captured",
                "client_id": client.id,
                "lead_id": lead.id,
                "source": source,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "client_id": client.id,
                "lead_id": lead.id,
                "stage": "LEAD",
                "next_action": lead.next_action
            }
    
    async def qualify_lead(
        self,
        lead_id: int
    ) -> Dict[str, Any]:
        """
        ML scoring and auto-qualification (>70 score)
        """
        async with async_session() as session:
            result = await session.execute(
                select(Lead, Client)
                .join(Client)
                .where(Lead.id == lead_id)
            )
            row = result.first()
            if not row:
                raise ValueError(f"Lead {lead_id} not found")
            
            lead, client = row
            
            client_data = {
                "email": client.email,
                "company": client.company,
                "industry": client.industry,
                "budget": lead.budget,
                "budget_range": client.budget_range,
                "source": client.source,
                "requirements": lead.requirements,
                "timeline": lead.timeline
            }
            
            qualification = await self.consulting_engine.qualify_lead(client_data)
            
            score = qualification["score"]
            qualified = qualification["qualified"]
            
            new_stage = "QUALIFIED" if qualified else "LEAD"
            probability = score / 100.0
            value_estimate = lead.budget or (5000 if score > 70 else 2000)
            
            await session.execute(
                update(Lead)
                .where(Lead.id == lead_id)
                .values(
                    score=score,
                    stage=new_stage,
                    probability=probability,
                    value_estimate=value_estimate,
                    ml_features=qualification["features"],
                    qualified_at=datetime.utcnow() if qualified else None,
                    next_action="Generate proposal" if qualified else "Nurture lead"
                )
            )
            await session.commit()
            
            await self.audit.log(
                action="lead_qualified",
                user="client_pipeline",
                details={
                    "lead_id": lead_id,
                    "score": score,
                    "qualified": qualified
                }
            )
            
            await self.ws_manager.broadcast({
                "type": "lead_qualified",
                "lead_id": lead_id,
                "score": score,
                "qualified": qualified,
                "stage": new_stage
            })
            
            return {
                "lead_id": lead_id,
                "score": score,
                "qualified": qualified,
                "stage": new_stage,
                "recommendation": qualification["recommendation"]
            }
    
    async def move_to_stage(
        self,
        lead_id: int,
        new_stage: str
    ) -> Dict[str, Any]:
        """Pipeline progression with validation"""
        if new_stage not in self.STAGES and new_stage not in self.LOST_STAGES:
            raise ValueError(f"Invalid stage: {new_stage}")
        
        async with async_session() as session:
            result = await session.execute(
                select(Lead).where(Lead.id == lead_id)
            )
            lead = result.scalar_one_or_none()
            if not lead:
                raise ValueError(f"Lead {lead_id} not found")
            
            old_stage = lead.stage
            
            updates = {"stage": new_stage}
            
            if new_stage == "PROPOSAL":
                updates["next_action"] = "Send proposal for approval"
            elif new_stage == "CONTRACT":
                updates["next_action"] = "Send contract for signature"
            elif new_stage == "ACTIVE":
                updates["next_action"] = "Begin project delivery"
            elif new_stage == "PAID":
                updates["converted_at"] = datetime.utcnow()
            elif new_stage in self.LOST_STAGES:
                updates["lost_at"] = datetime.utcnow()
            
            await session.execute(
                update(Lead)
                .where(Lead.id == lead_id)
                .values(**updates)
            )
            await session.commit()
            
            await self.audit.log(
                action="stage_changed",
                user="client_pipeline",
                details={
                    "lead_id": lead_id,
                    "old_stage": old_stage,
                    "new_stage": new_stage
                }
            )
            
            await self.ws_manager.broadcast({
                "type": "stage_changed",
                "lead_id": lead_id,
                "old_stage": old_stage,
                "new_stage": new_stage,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "lead_id": lead_id,
                "old_stage": old_stage,
                "new_stage": new_stage,
                "next_action": updates.get("next_action")
            }
    
    async def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Conversion rates per stage and overall metrics"""
        async with async_session() as session:
            total_leads = await session.execute(
                select(func.count(Lead.id))
            )
            total = total_leads.scalar()
            
            stage_counts = {}
            for stage in self.STAGES:
                result = await session.execute(
                    select(func.count(Lead.id)).where(Lead.stage == stage)
                )
                stage_counts[stage] = result.scalar()
            
            converted_result = await session.execute(
                select(func.count(Lead.id)).where(Lead.converted_at.isnot(None))
            )
            converted = converted_result.scalar()
            
            lost_result = await session.execute(
                select(func.count(Lead.id)).where(Lead.lost_at.isnot(None))
            )
            lost = lost_result.scalar()
            
            avg_score_result = await session.execute(
                select(func.avg(Lead.score))
            )
            avg_score = avg_score_result.scalar() or 0.0
            
            total_value_result = await session.execute(
                select(func.sum(Lead.value_estimate))
                .where(Lead.stage.in_(["QUALIFIED", "PROPOSAL", "NEGOTIATION", "CONTRACT", "ACTIVE"]))
            )
            total_value = total_value_result.scalar() or 0.0
            
            revenue_result = await session.execute(
                select(func.sum(Project.budget))
                .where(Project.status.in_(["completed", "delivered"]))
            )
            revenue = revenue_result.scalar() or 0.0
            
            conversion_rate = (converted / total * 100) if total > 0 else 0.0
            
            funnel = {}
            for i, stage in enumerate(self.STAGES[:-1]):
                current_count = stage_counts.get(stage, 0)
                next_stage = self.STAGES[i + 1]
                next_count = stage_counts.get(next_stage, 0)
                
                if current_count > 0:
                    funnel[f"{stage}_to_{next_stage}"] = (next_count / current_count) * 100
                else:
                    funnel[f"{stage}_to_{next_stage}"] = 0.0
            
            return {
                "total_leads": total,
                "converted": converted,
                "lost": lost,
                "conversion_rate": round(conversion_rate, 2),
                "avg_lead_score": round(avg_score, 2),
                "pipeline_value": round(total_value, 2),
                "revenue": round(revenue, 2),
                "stage_counts": stage_counts,
                "funnel_conversion": funnel,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def predict_close_rate(
        self,
        lead_id: int
    ) -> Dict[str, Any]:
        """ML prediction of lead conversion probability"""
        async with async_session() as session:
            result = await session.execute(
                select(Lead, Client)
                .join(Client)
                .where(Lead.id == lead_id)
            )
            row = result.first()
            if not row:
                raise ValueError(f"Lead {lead_id} not found")
            
            lead, client = row
            
            base_probability = lead.score / 100.0
            
            stage_multipliers = {
                "LEAD": 0.1,
                "QUALIFIED": 0.3,
                "PROPOSAL": 0.5,
                "NEGOTIATION": 0.7,
                "CONTRACT": 0.9,
                "ACTIVE": 0.95
            }
            
            stage_factor = stage_multipliers.get(lead.stage, 0.1)
            
            source_factors = {
                "referral": 1.3,
                "repeat": 1.5,
                "upwork": 0.9,
                "website": 0.8,
                "cold": 0.5
            }
            source_factor = source_factors.get(client.source, 1.0)
            
            budget_factor = 1.0
            if lead.budget:
                if lead.budget > 10000:
                    budget_factor = 1.2
                elif lead.budget < 2000:
                    budget_factor = 0.7
            
            final_probability = min(
                base_probability * stage_factor * source_factor * budget_factor,
                0.99
            )
            
            days_to_close = None
            if final_probability > 0.5:
                days_to_close = int(30 / final_probability)
            
            return {
                "lead_id": lead_id,
                "close_probability": round(final_probability, 3),
                "confidence": "high" if lead.score > 80 else "medium" if lead.score > 60 else "low",
                "estimated_days_to_close": days_to_close,
                "estimated_value": lead.value_estimate,
                "factors": {
                    "base_score": lead.score,
                    "stage": lead.stage,
                    "source": client.source,
                    "budget": lead.budget
                }
            }
    
    async def suggest_next_action(
        self,
        lead_id: int
    ) -> Dict[str, Any]:
        """Grace recommends what to do next"""
        async with async_session() as session:
            result = await session.execute(
                select(Lead, Client)
                .join(Client)
                .where(Lead.id == lead_id)
            )
            row = result.first()
            if not row:
                raise ValueError(f"Lead {lead_id} not found")
            
            lead, client = row
            
            actions = {
                "LEAD": {
                    "action": "Qualify this lead using ML scoring",
                    "priority": "high" if lead.budget and lead.budget > 5000 else "medium",
                    "automated": True,
                    "approval_needed": False
                },
                "QUALIFIED": {
                    "action": "Generate and send proposal",
                    "priority": "high",
                    "automated": True,
                    "approval_needed": lead.budget > 5000
                },
                "PROPOSAL": {
                    "action": "Follow up on proposal (Grace can draft email)",
                    "priority": "medium",
                    "automated": True,
                    "approval_needed": True
                },
                "NEGOTIATION": {
                    "action": "Address objections and finalize terms",
                    "priority": "high",
                    "automated": False,
                    "approval_needed": True
                },
                "CONTRACT": {
                    "action": "Send contract for signature",
                    "priority": "critical",
                    "automated": True,
                    "approval_needed": False
                },
                "ACTIVE": {
                    "action": "Begin project delivery with Grace Architect",
                    "priority": "critical",
                    "automated": True,
                    "approval_needed": lead.budget > 5000
                }
            }
            
            suggestion = actions.get(lead.stage, {
                "action": "Review lead status",
                "priority": "low",
                "automated": False,
                "approval_needed": True
            })
            
            if lead.next_action_date and lead.next_action_date < datetime.utcnow():
                suggestion["urgent"] = True
                suggestion["message"] = f"OVERDUE: {lead.next_action}"
            else:
                suggestion["urgent"] = False
                suggestion["message"] = suggestion["action"]
            
            return {
                "lead_id": lead_id,
                "current_stage": lead.stage,
                "suggestion": suggestion,
                "can_automate": suggestion["automated"],
                "needs_approval": suggestion["approval_needed"],
                "timestamp": datetime.utcnow().isoformat()
            }
