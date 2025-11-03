"""Marketplace Connector for Upwork and Fiverr

Automated job discovery, proposal generation, and client communication.
Integrates with Hunter for job analysis and Parliament for approval.
"""

import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ...models import async_session
from .models import (
    MarketplaceJob,
    MarketplaceProposal,
    MarketplaceMessage,
    MarketplaceDeliverable
)
from ...secrets_vault import secrets_vault
from ...immutable_log import ImmutableLogger
from ...governance import GovernanceEngine


class MarketplaceConnector:
    """Connector for Upwork and Fiverr marketplaces"""
    
    def __init__(self):
        self.logger = ImmutableLogger()
        self.governance = GovernanceEngine()
        self._upwork_client = None
        self._fiverr_client = None
    
    async def _initialize_upwork(self) -> bool:
        """Initialize Upwork API client"""
        try:
            oauth_token = await secrets_vault.retrieve_secret(
                key="upwork_oauth_token",
                accessor="marketplace_connector",
                purpose="job_search"
            )
            
            if not oauth_token:
                await self.logger.log(
                    event_type="upwork_init_failed",
                    data={"reason": "OAuth token not found"},
                    actor="marketplace_connector"
                )
                return False
            
            # TODO: Initialize actual Upwork client when credentials are available
            # from upwork import Client
            # self._upwork_client = Client(oauth_token)
            
            self._upwork_client = "mock_client"  # Placeholder
            
            await self.logger.log(
                event_type="upwork_initialized",
                data={"timestamp": datetime.utcnow().isoformat()},
                actor="marketplace_connector"
            )
            
            return True
            
        except Exception as e:
            await self.logger.log(
                event_type="upwork_init_error",
                data={"error": str(e)},
                actor="marketplace_connector"
            )
            return False
    
    async def _initialize_fiverr(self) -> bool:
        """Initialize Fiverr API client"""
        try:
            api_key = await secrets_vault.retrieve_secret(
                key="fiverr_api_key",
                accessor="marketplace_connector",
                purpose="marketplace_integration"
            )
            
            if not api_key:
                await self.logger.log(
                    event_type="fiverr_init_failed",
                    data={"reason": "API key not found"},
                    actor="marketplace_connector"
                )
                return False
            
            # TODO: Initialize actual Fiverr client when credentials are available
            self._fiverr_client = "mock_client"  # Placeholder
            
            await self.logger.log(
                event_type="fiverr_initialized",
                data={"timestamp": datetime.utcnow().isoformat()},
                actor="marketplace_connector"
            )
            
            return True
            
        except Exception as e:
            await self.logger.log(
                event_type="fiverr_init_error",
                data={"error": str(e)},
                actor="marketplace_connector"
            )
            return False
    
    # ========== UPWORK METHODS ==========
    
    async def search_jobs(
        self,
        keywords: str,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant jobs on Upwork
        
        Args:
            keywords: Search keywords
            budget_min: Minimum budget filter
            budget_max: Maximum budget filter
            category: Job category
            limit: Maximum results
            
        Returns:
            List of job matches
        """
        async with async_session() as session:
            try:
                if not await self._initialize_upwork():
                    return []
                
                # TODO: Actual Upwork API call when credentials are available
                # jobs_data = self._upwork_client.search_jobs(
                #     q=keywords,
                #     budget_min=budget_min,
                #     budget_max=budget_max,
                #     category=category,
                #     limit=limit
                # )
                
                # Mock data for development
                jobs_data = self._mock_upwork_jobs(keywords, budget_min, limit)
                
                jobs = []
                for job_data in jobs_data:
                    # Check if already exists
                    result = await session.execute(
                        select(MarketplaceJob).where(
                            MarketplaceJob.job_id == job_data["id"]
                        )
                    )
                    existing = result.scalar_one_or_none()
                    
                    if not existing:
                        # Create new job record
                        job = MarketplaceJob(
                            platform="upwork",
                            job_id=job_data["id"],
                            title=job_data["title"],
                            description=job_data["description"],
                            budget=job_data.get("budget"),
                            budget_type=job_data.get("budget_type", "fixed"),
                            client_id=job_data.get("client_id"),
                            client_name=job_data.get("client_name"),
                            client_rating=job_data.get("client_rating"),
                            status="discovered",
                            skills_required=job_data.get("skills", []),
                            metadata=job_data
                        )
                        
                        session.add(job)
                        jobs.append(job_data)
                    else:
                        jobs.append(job_data)
                
                await session.commit()
                
                # Log search
                await self.logger.log(
                    event_type="upwork_jobs_searched",
                    data={
                        "keywords": keywords,
                        "found": len(jobs),
                        "budget_min": budget_min
                    },
                    actor="marketplace_connector"
                )
                
                return jobs
                
            except Exception as e:
                await self.logger.log(
                    event_type="upwork_search_error",
                    data={"error": str(e), "keywords": keywords},
                    actor="marketplace_connector"
                )
                return []
    
    async def submit_proposal(
        self,
        job_id: str,
        proposal_text: str,
        bid_amount: Optional[float] = None,
        estimated_hours: Optional[int] = None,
        governance_approved: bool = False
    ) -> Dict[str, Any]:
        """
        Submit proposal to Upwork job
        
        Args:
            job_id: Job identifier
            proposal_text: Proposal content
            bid_amount: Bid amount
            estimated_hours: Time estimate
            governance_approved: Whether governance approved
            
        Returns:
            Submission result
        """
        async with async_session() as session:
            try:
                # Get job
                result = await session.execute(
                    select(MarketplaceJob).where(
                        MarketplaceJob.job_id == job_id
                    )
                )
                job = result.scalar_one_or_none()
                
                if not job:
                    return {
                        "success": False,
                        "error": "Job not found"
                    }
                
                # Check governance approval
                if not governance_approved:
                    await self.logger.log(
                        event_type="proposal_requires_approval",
                        data={
                            "job_id": job_id,
                            "job_title": job.title,
                            "bid_amount": bid_amount
                        },
                        actor="marketplace_connector"
                    )
                    
                    # Create draft proposal
                    proposal = MarketplaceProposal(
                        job_id=job.id,
                        marketplace_job_id=job_id,
                        platform="upwork",
                        proposal_text=proposal_text,
                        bid_amount=bid_amount,
                        estimated_hours=estimated_hours,
                        status="draft",
                        governance_approved=False
                    )
                    
                    session.add(proposal)
                    await session.commit()
                    
                    return {
                        "success": False,
                        "error": "Governance approval required",
                        "proposal_id": proposal.id,
                        "requires_approval": True
                    }
                
                if not await self._initialize_upwork():
                    return {
                        "success": False,
                        "error": "Upwork not initialized"
                    }
                
                # TODO: Actual Upwork API call
                # result = self._upwork_client.submit_proposal(
                #     job_id=job_id,
                #     cover_letter=proposal_text,
                #     bid_amount=bid_amount,
                #     estimated_hours=estimated_hours
                # )
                
                # Mock submission
                submission_result = {
                    "success": True,
                    "proposal_id": f"proposal_{job_id}",
                    "submitted_at": datetime.utcnow().isoformat()
                }
                
                # Create proposal record
                proposal = MarketplaceProposal(
                    job_id=job.id,
                    marketplace_job_id=job_id,
                    platform="upwork",
                    proposal_text=proposal_text,
                    bid_amount=bid_amount,
                    estimated_hours=estimated_hours,
                    status="submitted",
                    governance_approved=True,
                    submitted_at=datetime.utcnow()
                )
                
                session.add(proposal)
                
                # Update job status
                job.status = "applied"
                
                await session.commit()
                
                # Log submission
                await self.logger.log(
                    event_type="proposal_submitted",
                    data={
                        "job_id": job_id,
                        "job_title": job.title,
                        "bid_amount": bid_amount,
                        "proposal_id": proposal.id
                    },
                    actor="marketplace_connector"
                )
                
                return {
                    "success": True,
                    "proposal_id": proposal.id,
                    "job_title": job.title,
                    "submitted_at": proposal.submitted_at
                }
                
            except Exception as e:
                await self.logger.log(
                    event_type="proposal_submission_error",
                    data={"error": str(e), "job_id": job_id},
                    actor="marketplace_connector"
                )
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def get_messages(
        self,
        client_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch messages from client
        
        Args:
            client_id: Client identifier
            limit: Maximum messages
            
        Returns:
            List of messages
        """
        async with async_session() as session:
            try:
                if not await self._initialize_upwork():
                    return []
                
                # TODO: Actual Upwork API call
                # messages_data = self._upwork_client.get_messages(
                #     client_id=client_id,
                #     limit=limit
                # )
                
                # Get from database
                result = await session.execute(
                    select(MarketplaceMessage)
                    .where(MarketplaceMessage.client_id == client_id)
                    .where(MarketplaceMessage.platform == "upwork")
                    .order_by(desc(MarketplaceMessage.created_at))
                    .limit(limit)
                )
                messages = result.scalars().all()
                
                return [
                    {
                        "id": msg.id,
                        "direction": msg.direction,
                        "message": msg.message_text,
                        "created_at": msg.created_at.isoformat(),
                        "auto_generated": msg.auto_generated
                    }
                    for msg in messages
                ]
                
            except Exception as e:
                await self.logger.log(
                    event_type="get_messages_error",
                    data={"error": str(e), "client_id": client_id},
                    actor="marketplace_connector"
                )
                return []
    
    async def respond_to_message(
        self,
        client_id: str,
        response: str,
        job_id: Optional[str] = None,
        auto_approved: bool = False
    ) -> Dict[str, Any]:
        """
        Send response to client message
        
        Args:
            client_id: Client identifier
            response: Response text
            job_id: Optional job context
            auto_approved: Whether auto-approved by Grace
            
        Returns:
            Response result
        """
        async with async_session() as session:
            try:
                if not await self._initialize_upwork():
                    return {
                        "success": False,
                        "error": "Upwork not initialized"
                    }
                
                # TODO: Actual Upwork API call
                # result = self._upwork_client.send_message(
                #     client_id=client_id,
                #     message=response
                # )
                
                # Store message
                job_record = None
                if job_id:
                    result = await session.execute(
                        select(MarketplaceJob).where(
                            MarketplaceJob.job_id == job_id
                        )
                    )
                    job_record = result.scalar_one_or_none()
                
                message = MarketplaceMessage(
                    job_id=job_record.id if job_record else None,
                    marketplace_job_id=job_id,
                    platform="upwork",
                    client_id=client_id,
                    direction="outbound",
                    message_text=response,
                    auto_generated=auto_approved,
                    grace_approved=auto_approved
                )
                
                session.add(message)
                await session.commit()
                
                # Log response
                await self.logger.log(
                    event_type="client_message_sent",
                    data={
                        "client_id": client_id,
                        "job_id": job_id,
                        "auto_generated": auto_approved
                    },
                    actor="marketplace_connector"
                )
                
                return {
                    "success": True,
                    "message_id": message.id,
                    "sent_at": message.created_at.isoformat()
                }
                
            except Exception as e:
                await self.logger.log(
                    event_type="send_message_error",
                    data={"error": str(e), "client_id": client_id},
                    actor="marketplace_connector"
                )
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def accept_contract(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """
        Accept a contract/job offer
        
        Args:
            job_id: Job identifier
            
        Returns:
            Acceptance result
        """
        async with async_session() as session:
            try:
                if not await self._initialize_upwork():
                    return {
                        "success": False,
                        "error": "Upwork not initialized"
                    }
                
                # Get job
                result = await session.execute(
                    select(MarketplaceJob).where(
                        MarketplaceJob.job_id == job_id
                    )
                )
                job = result.scalar_one_or_none()
                
                if not job:
                    return {
                        "success": False,
                        "error": "Job not found"
                    }
                
                # TODO: Actual Upwork API call
                # result = self._upwork_client.accept_offer(job_id=job_id)
                
                # Update status
                job.status = "in_progress"
                await session.commit()
                
                # Log acceptance
                await self.logger.log(
                    event_type="contract_accepted",
                    data={
                        "job_id": job_id,
                        "job_title": job.title,
                        "budget": job.budget
                    },
                    actor="marketplace_connector"
                )
                
                return {
                    "success": True,
                    "job_id": job_id,
                    "status": "in_progress"
                }
                
            except Exception as e:
                await self.logger.log(
                    event_type="accept_contract_error",
                    data={"error": str(e), "job_id": job_id},
                    actor="marketplace_connector"
                )
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def submit_work(
        self,
        job_id: str,
        deliverables: List[str],
        description: str
    ) -> Dict[str, Any]:
        """
        Submit work deliverables
        
        Args:
            job_id: Job identifier
            deliverables: List of file paths
            description: Delivery description
            
        Returns:
            Submission result
        """
        async with async_session() as session:
            try:
                # Get job
                result = await session.execute(
                    select(MarketplaceJob).where(
                        MarketplaceJob.job_id == job_id
                    )
                )
                job = result.scalar_one_or_none()
                
                if not job:
                    return {
                        "success": False,
                        "error": "Job not found"
                    }
                
                if not await self._initialize_upwork():
                    return {
                        "success": False,
                        "error": "Upwork not initialized"
                    }
                
                # TODO: Actual Upwork API call to submit files
                # result = self._upwork_client.submit_work(
                #     job_id=job_id,
                #     files=deliverables,
                #     message=description
                # )
                
                # Create deliverable record
                deliverable = MarketplaceDeliverable(
                    job_id=job.id,
                    marketplace_job_id=job_id,
                    platform="upwork",
                    title=f"Deliverable for {job.title}",
                    description=description,
                    file_paths=deliverables,
                    status="submitted",
                    submitted_at=datetime.utcnow()
                )
                
                session.add(deliverable)
                
                # Update job status
                job.status = "completed"
                
                await session.commit()
                
                # Log submission
                await self.logger.log(
                    event_type="work_submitted",
                    data={
                        "job_id": job_id,
                        "job_title": job.title,
                        "files_count": len(deliverables)
                    },
                    actor="marketplace_connector"
                )
                
                return {
                    "success": True,
                    "deliverable_id": deliverable.id,
                    "submitted_at": deliverable.submitted_at.isoformat()
                }
                
            except Exception as e:
                await self.logger.log(
                    event_type="submit_work_error",
                    data={"error": str(e), "job_id": job_id},
                    actor="marketplace_connector"
                )
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def request_payment(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """
        Request payment for completed work
        
        Args:
            job_id: Job identifier
            
        Returns:
            Payment request result
        """
        async with async_session() as session:
            try:
                # Get job
                result = await session.execute(
                    select(MarketplaceJob).where(
                        MarketplaceJob.job_id == job_id
                    )
                )
                job = result.scalar_one_or_none()
                
                if not job:
                    return {
                        "success": False,
                        "error": "Job not found"
                    }
                
                if job.status != "completed":
                    return {
                        "success": False,
                        "error": "Job not completed"
                    }
                
                if not await self._initialize_upwork():
                    return {
                        "success": False,
                        "error": "Upwork not initialized"
                    }
                
                # TODO: Actual Upwork API call
                # result = self._upwork_client.request_payment(job_id=job_id)
                
                # Update status
                job.status = "paid"
                await session.commit()
                
                # Log payment request
                await self.logger.log(
                    event_type="payment_requested",
                    data={
                        "job_id": job_id,
                        "job_title": job.title,
                        "amount": job.budget
                    },
                    actor="marketplace_connector"
                )
                
                return {
                    "success": True,
                    "job_id": job_id,
                    "amount": job.budget,
                    "status": "paid"
                }
                
            except Exception as e:
                await self.logger.log(
                    event_type="request_payment_error",
                    data={"error": str(e), "job_id": job_id},
                    actor="marketplace_connector"
                )
                return {
                    "success": False,
                    "error": str(e)
                }
    
    # ========== FIVERR METHODS ==========
    
    async def create_gig(
        self,
        title: str,
        description: str,
        price: float,
        delivery_days: int = 7,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a gig on Fiverr
        
        Args:
            title: Gig title
            description: Gig description
            price: Gig price
            delivery_days: Delivery time
            category: Gig category
            
        Returns:
            Gig creation result
        """
        try:
            if not await self._initialize_fiverr():
                return {
                    "success": False,
                    "error": "Fiverr not initialized"
                }
            
            # TODO: Actual Fiverr API call when available
            # result = self._fiverr_client.create_gig(
            #     title=title,
            #     description=description,
            #     price=price,
            #     delivery_days=delivery_days,
            #     category=category
            # )
            
            gig_data = {
                "gig_id": f"gig_{datetime.utcnow().timestamp()}",
                "title": title,
                "price": price,
                "url": f"https://fiverr.com/gig/{title.lower().replace(' ', '-')}"
            }
            
            # Log gig creation
            await self.logger.log(
                event_type="fiverr_gig_created",
                data={
                    "title": title,
                    "price": price,
                    "delivery_days": delivery_days
                },
                actor="marketplace_connector"
            )
            
            return {
                "success": True,
                **gig_data
            }
            
        except Exception as e:
            await self.logger.log(
                event_type="create_gig_error",
                data={"error": str(e), "title": title},
                actor="marketplace_connector"
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def manage_orders(self) -> List[Dict[str, Any]]:
        """
        Get incoming Fiverr orders
        
        Returns:
            List of active orders
        """
        try:
            if not await self._initialize_fiverr():
                return []
            
            # TODO: Actual Fiverr API call
            # orders = self._fiverr_client.get_orders(status="active")
            
            # Mock orders
            orders = []
            
            return orders
            
        except Exception as e:
            await self.logger.log(
                event_type="manage_orders_error",
                data={"error": str(e)},
                actor="marketplace_connector"
            )
            return []
    
    async def deliver_order(
        self,
        order_id: str,
        files: List[str],
        message: str
    ) -> Dict[str, Any]:
        """
        Deliver completed Fiverr order
        
        Args:
            order_id: Order identifier
            files: Deliverable files
            message: Delivery message
            
        Returns:
            Delivery result
        """
        try:
            if not await self._initialize_fiverr():
                return {
                    "success": False,
                    "error": "Fiverr not initialized"
                }
            
            # TODO: Actual Fiverr API call
            # result = self._fiverr_client.deliver_order(
            #     order_id=order_id,
            #     files=files,
            #     message=message
            # )
            
            # Log delivery
            await self.logger.log(
                event_type="fiverr_order_delivered",
                data={
                    "order_id": order_id,
                    "files_count": len(files)
                },
                actor="marketplace_connector"
            )
            
            return {
                "success": True,
                "order_id": order_id,
                "delivered_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            await self.logger.log(
                event_type="deliver_order_error",
                data={"error": str(e), "order_id": order_id},
                actor="marketplace_connector"
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========== HELPER METHODS ==========
    
    def _mock_upwork_jobs(
        self,
        keywords: str,
        budget_min: Optional[float],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Generate mock Upwork jobs for development"""
        jobs = [
            {
                "id": f"upwork_job_1_{datetime.utcnow().timestamp()}",
                "title": "Python Web Scraping Project",
                "description": "Need someone to scrape data from multiple websites and store in database.",
                "budget": 500.0,
                "budget_type": "fixed",
                "client_id": "client_001",
                "client_name": "TechCorp Inc",
                "client_rating": 4.8,
                "skills": ["Python", "Web Scraping", "BeautifulSoup", "Selenium"]
            },
            {
                "id": f"upwork_job_2_{datetime.utcnow().timestamp()}",
                "title": "AI Chatbot Development",
                "description": "Looking for developer to build intelligent chatbot using GPT API.",
                "budget": 1200.0,
                "budget_type": "fixed",
                "client_id": "client_002",
                "client_name": "StartupXYZ",
                "client_rating": 4.5,
                "skills": ["Python", "AI", "OpenAI API", "FastAPI"]
            },
            {
                "id": f"upwork_job_3_{datetime.utcnow().timestamp()}",
                "title": "Database Optimization",
                "description": "Need expert to optimize PostgreSQL database performance.",
                "budget": 800.0,
                "budget_type": "fixed",
                "client_id": "client_003",
                "client_name": "DataCo",
                "client_rating": 4.9,
                "skills": ["PostgreSQL", "SQL", "Database Optimization"]
            }
        ]
        
        # Filter by budget
        if budget_min:
            jobs = [j for j in jobs if j["budget"] >= budget_min]
        
        return jobs[:limit]


# Singleton instance
marketplace_connector = MarketplaceConnector()
