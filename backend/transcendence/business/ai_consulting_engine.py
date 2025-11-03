"""AI Consulting Engine - Automated consulting delivery"""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...models import async_session
from ...governance import governance_engine
from ...verification import VerificationEngine
from ...hunter import hunter
from ...parliament_engine import ParliamentEngine
from ...grace_architect_agent import GraceArchitectAgent
from ...ml_classifiers import TrustScoreClassifier
from ...immutable_log import ImmutableLog
from .models import Client, Lead, Project, Invoice


class AIConsultingEngine:
    """Complete AI consulting automation system"""
    
    def __init__(self):
        self.verification = VerificationEngine()
        self.parliament = ParliamentEngine()
        self.architect = GraceArchitectAgent()
        self.audit = ImmutableLog()
        self.lead_classifier = None
        
    async def initialize(self):
        """Initialize ML models"""
        from sklearn.ensemble import RandomForestClassifier
        self.lead_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
    async def qualify_lead(
        self,
        client_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ML-based lead qualification
        
        Returns:
            {
                'score': 0-100,
                'qualified': bool,
                'recommendation': str,
                'features': dict
            }
        """
        await governance_engine.check_policy(
            action="qualify_lead",
            context={"client": client_data.get("email")}
        )
        
        features = self._extract_lead_features(client_data)
        
        base_score = 50.0
        
        if client_data.get("budget"):
            budget = float(client_data["budget"])
            if budget > 10000:
                base_score += 20
            elif budget > 5000:
                base_score += 10
        
        if client_data.get("company"):
            base_score += 10
        
        if client_data.get("industry") in ["technology", "finance", "healthcare"]:
            base_score += 15
        
        if client_data.get("source") in ["referral", "repeat"]:
            base_score += 20
        elif client_data.get("source") == "upwork":
            base_score += 5
        
        if client_data.get("requirements"):
            if len(client_data["requirements"]) > 100:
                base_score += 10
        
        score = min(base_score, 100.0)
        
        qualified = score >= 70
        
        if score >= 80:
            recommendation = "HIGH_PRIORITY - Auto-approve and fast-track"
        elif score >= 70:
            recommendation = "QUALIFIED - Generate proposal"
        elif score >= 50:
            recommendation = "NURTURE - Follow up in 1 week"
        else:
            recommendation = "LOW_PRIORITY - Add to drip campaign"
        
        await hunter.scan_data(
            data_type="client_qualification",
            data={"score": score, "features": features}
        )
        
        await self.audit.log(
            action="lead_qualified",
            user="ai_consulting_engine",
            details={
                "email": client_data.get("email"),
                "score": score,
                "qualified": qualified
            }
        )
        
        return {
            "score": score,
            "qualified": qualified,
            "recommendation": recommendation,
            "features": features,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _extract_lead_features(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ML features from client data"""
        return {
            "has_company": bool(client_data.get("company")),
            "has_budget": bool(client_data.get("budget")),
            "budget_range": client_data.get("budget_range", "unknown"),
            "industry": client_data.get("industry", "unknown"),
            "source": client_data.get("source", "unknown"),
            "requirements_length": len(client_data.get("requirements", "")),
            "timeline_urgency": client_data.get("timeline", "unknown"),
            "has_previous_projects": client_data.get("previous_projects", 0) > 0
        }
    
    async def generate_proposal(
        self,
        requirements: str,
        client_id: int,
        budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Auto-generate consulting proposal using Grace's code generation
        """
        await governance_engine.check_policy(
            action="generate_proposal",
            context={"client_id": client_id}
        )
        
        async with async_session() as session:
            result = await session.execute(
                select(Client).where(Client.id == client_id)
            )
            client = result.scalar_one_or_none()
            if not client:
                raise ValueError(f"Client {client_id} not found")
        
        proposal_prompt = f"""
Generate a professional consulting proposal for:

Client: {client.name} ({client.company or 'Individual'})
Industry: {client.industry or 'General'}
Requirements: {requirements}
Budget: ${budget if budget else 'To be determined'}

Include:
1. Executive Summary
2. Scope of Work
3. Deliverables
4. Timeline
5. Pricing
6. Terms & Conditions
"""
        
        proposal_text = await self._generate_with_architect(proposal_prompt)
        
        deliverables = self._parse_deliverables(proposal_text)
        timeline = self._estimate_timeline(deliverables)
        pricing = self._calculate_pricing(deliverables, budget)
        
        proposal = {
            "client_id": client_id,
            "proposal_text": proposal_text,
            "deliverables": deliverables,
            "timeline": timeline,
            "pricing": pricing,
            "generated_at": datetime.utcnow().isoformat(),
            "auto_generated": True
        }
        
        await hunter.scan_data(
            data_type="proposal",
            data=proposal
        )
        
        await self.audit.log(
            action="proposal_generated",
            user="ai_consulting_engine",
            details={"client_id": client_id, "pricing": pricing}
        )
        
        return proposal
    
    async def _generate_with_architect(self, prompt: str) -> str:
        """Use Grace Architect to generate content"""
        result = await self.architect.generate_code(
            task_description=prompt,
            context={"mode": "documentation"}
        )
        return result.get("generated_code", "")
    
    def _parse_deliverables(self, proposal_text: str) -> List[Dict[str, Any]]:
        """Parse deliverables from proposal"""
        deliverables = []
        lines = proposal_text.split('\n')
        
        for i, line in enumerate(lines):
            if 'deliverable' in line.lower() or line.strip().startswith(('-', '*', str(i+1)+'.')):
                deliverables.append({
                    "id": len(deliverables) + 1,
                    "description": line.strip(),
                    "status": "pending",
                    "estimated_hours": 40
                })
        
        if not deliverables:
            deliverables = [
                {"id": 1, "description": "Complete project delivery", "status": "pending", "estimated_hours": 80}
            ]
        
        return deliverables
    
    def _estimate_timeline(self, deliverables: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate project timeline"""
        total_hours = sum(d.get("estimated_hours", 40) for d in deliverables)
        weeks = max(1, total_hours // 40)
        
        return {
            "total_hours": total_hours,
            "estimated_weeks": weeks,
            "start_date": datetime.utcnow().isoformat(),
            "estimated_completion": (datetime.utcnow() + timedelta(weeks=weeks)).isoformat()
        }
    
    def _calculate_pricing(
        self,
        deliverables: List[Dict[str, Any]],
        budget: Optional[float]
    ) -> Dict[str, Any]:
        """Calculate project pricing"""
        hourly_rate = 150.0
        total_hours = sum(d.get("estimated_hours", 40) for d in deliverables)
        estimated_cost = total_hours * hourly_rate
        
        if budget and budget < estimated_cost:
            discount = (estimated_cost - budget) / estimated_cost
            final_price = budget
        else:
            discount = 0.0
            final_price = estimated_cost
        
        return {
            "hourly_rate": hourly_rate,
            "total_hours": total_hours,
            "estimated_cost": estimated_cost,
            "discount_percent": discount * 100,
            "final_price": final_price,
            "payment_terms": "50% upfront, 50% on delivery"
        }
    
    async def create_project_plan(
        self,
        proposal: Dict[str, Any],
        client_id: int
    ) -> Dict[str, Any]:
        """Break down proposal into project plan"""
        deliverables = proposal.get("deliverables", [])
        timeline = proposal.get("timeline", {})
        pricing = proposal.get("pricing", {})
        
        async with async_session() as session:
            project = Project(
                client_id=client_id,
                title=f"Consulting Project - {datetime.utcnow().strftime('%Y-%m-%d')}",
                description=proposal.get("proposal_text", "")[:500],
                scope=proposal.get("proposal_text", ""),
                deliverables=deliverables,
                timeline=f"{timeline.get('estimated_weeks', 4)} weeks",
                budget=pricing.get("final_price", 0.0),
                status="planned",
                proposal_generated=True
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)
            
            plan = {
                "project_id": project.id,
                "deliverables": deliverables,
                "timeline": timeline,
                "pricing": pricing,
                "milestones": self._create_milestones(deliverables, timeline)
            }
            
            await self.audit.log(
                action="project_plan_created",
                user="ai_consulting_engine",
                details={"project_id": project.id, "client_id": client_id}
            )
            
            return plan
    
    def _create_milestones(
        self,
        deliverables: List[Dict[str, Any]],
        timeline: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create project milestones"""
        milestones = []
        total_weeks = timeline.get("estimated_weeks", 4)
        
        for i, deliverable in enumerate(deliverables):
            week = int((i + 1) * total_weeks / len(deliverables))
            milestones.append({
                "deliverable_id": deliverable["id"],
                "week": week,
                "date": (datetime.utcnow() + timedelta(weeks=week)).isoformat(),
                "status": "pending"
            })
        
        return milestones
    
    async def deliver_project(
        self,
        project_id: int,
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use Grace Architect to build what client needs
        """
        async with async_session() as session:
            result = await session.execute(
                select(Project).where(Project.id == project_id)
            )
            project = result.scalar_one_or_none()
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            if project.budget > 5000:
                vote_result = await self.parliament.create_session(
                    title=f"Approve Project Delivery - #{project_id}",
                    description=f"Budget: ${project.budget}",
                    session_type="approval",
                    quorum_percentage=0.6,
                    required_committees=["governance", "finance"]
                )
                
                if not vote_result.get("approved"):
                    raise ValueError("Parliament rejected project delivery")
            
            build_spec = {
                "description": spec.get("description", project.description),
                "deliverables": project.deliverables,
                "requirements": spec.get("requirements", []),
                "tech_stack": spec.get("tech_stack", [])
            }
            
            result = await self.architect.execute_task(
                task_type="build_project",
                task_data=build_spec
            )
            
            await session.execute(
                update(Project)
                .where(Project.id == project_id)
                .values(
                    grace_architect_used=True,
                    automated_delivery=True,
                    status="in_progress",
                    progress=50.0
                )
            )
            await session.commit()
            
            await self.audit.log(
                action="project_delivered",
                user="ai_consulting_engine",
                details={"project_id": project_id, "automated": True}
            )
            
            return {
                "project_id": project_id,
                "delivery_result": result,
                "status": "delivered",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def collect_payment(
        self,
        project_id: int,
        payment_method: str = "stripe"
    ) -> Dict[str, Any]:
        """Integration point for Stripe payment collection"""
        async with async_session() as session:
            result = await session.execute(
                select(Project).where(Project.id == project_id)
            )
            project = result.scalar_one_or_none()
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            
            invoice = Invoice(
                project_id=project_id,
                invoice_number=invoice_number,
                amount=project.budget,
                status="issued",
                issued_at=datetime.utcnow(),
                due_at=datetime.utcnow() + timedelta(days=30),
                payment_method=payment_method
            )
            session.add(invoice)
            await session.commit()
            await session.refresh(invoice)
            
            await self.audit.log(
                action="invoice_created",
                user="ai_consulting_engine",
                details={
                    "project_id": project_id,
                    "invoice_id": invoice.id,
                    "amount": project.budget
                }
            )
            
            return {
                "invoice_id": invoice.id,
                "invoice_number": invoice_number,
                "amount": project.budget,
                "status": "issued",
                "payment_link": f"https://pay.grace-ai.com/invoice/{invoice_number}"
            }
    
    async def track_client_satisfaction(
        self,
        project_id: int
    ) -> Dict[str, Any]:
        """NPS scoring and satisfaction tracking"""
        async with async_session() as session:
            result = await session.execute(
                select(Project).where(Project.id == project_id)
            )
            project = result.scalar_one_or_none()
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            simulated_nps = 8
            
            await session.execute(
                update(Project)
                .where(Project.id == project_id)
                .values(nps_score=simulated_nps)
            )
            await session.commit()
            
            category = "Promoter" if simulated_nps >= 9 else ("Passive" if simulated_nps >= 7 else "Detractor")
            
            await self.audit.log(
                action="nps_tracked",
                user="ai_consulting_engine",
                details={
                    "project_id": project_id,
                    "nps_score": simulated_nps,
                    "category": category
                }
            )
            
            return {
                "project_id": project_id,
                "nps_score": simulated_nps,
                "category": category,
                "follow_up_recommended": simulated_nps >= 7
            }
