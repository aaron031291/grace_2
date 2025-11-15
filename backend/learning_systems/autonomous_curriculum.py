"""
Autonomous Learning Curriculum
Grace learns by building real projects, mastering each topic through practice
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class KnowledgeDomain:
    """Represents a knowledge domain to master"""
    def __init__(
        self,
        domain_id: str,
        name: str,
        topics: List[str],
        learning_projects: List[Dict[str, Any]],
        prerequisites: Optional[List[str]] = None
    ):
        self.domain_id = domain_id
        self.name = name
        self.topics = topics
        self.learning_projects = learning_projects
        self.prerequisites = prerequisites or []
        self.mastery_level = 0.0  # 0-100%
        self.projects_completed = []
        self.skills_acquired = []


class LearningProject:
    """A real project Grace builds to learn"""
    def __init__(
        self,
        project_id: str,
        name: str,
        description: str,
        domain: str,
        objectives: List[str],
        success_criteria: Dict[str, Any],
        estimated_complexity: int  # 1-10
    ):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.domain = domain
        self.objectives = objectives
        self.success_criteria = success_criteria
        self.estimated_complexity = estimated_complexity
        self.status = "not_started"  # not_started, in_progress, completed, failed
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.trust_score = 0.0
        self.kpis: Dict[str, float] = {}
        self.learnings: List[str] = []


class AutonomousCurriculum:
    """
    Grace's autonomous learning curriculum
    She learns by building real projects, understanding edge cases in sandbox
    """
    
    def __init__(self):
        self.domains: Dict[str, KnowledgeDomain] = {}
        self.projects: Dict[str, LearningProject] = {}
        self.current_focus: Optional[str] = None
        self.learning_mode = "project_based"  # project_based, exploratory, research
        
        # Learning progress
        self.total_domains = 0
        self.domains_mastered = 0
        self.projects_completed = 0
        self.total_learning_hours = 0
        
        # Storage
        self.storage_path = Path("databases/learning_curriculum")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._initialize_curriculum()
        self._load_progress()
    
    def _initialize_curriculum(self):
        """Initialize the complete knowledge base curriculum"""
        
        # Domain 1: Programming & Software Engineering
        self.domains["programming"] = KnowledgeDomain(
            domain_id="programming",
            name="Programming & Software Engineering",
            topics=[
                "Python advanced patterns",
                "Java/C++/Go/Rust systems programming",
                "TypeScript/JavaScript full-stack",
                "Functional programming",
                "Concurrent/parallel programming",
                "Design patterns (GoF, microservices, CQRS)",
                "Testing (unit, integration, E2E, property-based)",
                "Compilers and interpreters"
            ],
            learning_projects=[
                {
                    "id": "proj_compiler",
                    "name": "Build a Programming Language Compiler",
                    "description": "Create a simple compiled language from scratch",
                    "objectives": ["Lexer", "Parser", "AST", "Code generation", "Runtime"],
                    "complexity": 8
                },
                {
                    "id": "proj_async_framework",
                    "name": "Async I/O Framework",
                    "description": "Build event loop, async/await, concurrent executor",
                    "objectives": ["Event loop", "Futures/Promises", "Thread pool", "Benchmarks"],
                    "complexity": 7
                }
            ],
            prerequisites=[]
        )
        
        # Domain 2: Data Engineering & Analytics
        self.domains["data_engineering"] = KnowledgeDomain(
            domain_id="data_engineering",
            name="Data Engineering & Analytics",
            topics=[
                "Data pipelines (batch, streaming)",
                "Databases (SQL, NoSQL, time-series, graph)",
                "ETL/ELT frameworks",
                "Data modeling (OLTP, OLAP, dimensional)",
                "Data quality & governance",
                "Real-time streaming (Kafka-like)",
                "Data warehousing",
                "Lakehouse architecture"
            ],
            learning_projects=[
                {
                    "id": "proj_data_pipeline",
                    "name": "Real-Time Data Pipeline Engine",
                    "description": "Build streaming data pipeline with quality checks",
                    "objectives": ["Ingestion", "Transformation", "Quality gates", "Monitoring"],
                    "complexity": 9
                },
                {
                    "id": "proj_olap_engine",
                    "name": "Columnar OLAP Query Engine",
                    "description": "Build analytical query engine with aggregations",
                    "objectives": ["Columnar storage", "Query optimizer", "Aggregations", "Benchmarks"],
                    "complexity": 10
                }
            ],
            prerequisites=["programming"]
        )
        
        # Domain 3: Cloud Infrastructure (PRIORITY PROJECT)
        self.domains["cloud_infrastructure"] = KnowledgeDomain(
            domain_id="cloud_infrastructure",
            name="Cloud Platforms & Infrastructure",
            topics=[
                "Cloud providers (AWS, Azure, GCP)",
                "Compute, storage, networking",
                "Serverless architectures",
                "Container orchestration (Kubernetes)",
                "Infrastructure as Code",
                "Auto-scaling and cost optimization",
                "Multi-cloud strategies",
                "Edge computing"
            ],
            learning_projects=[
                {
                    "id": "proj_cloud_infra_scratch",
                    "name": "Cloud Infrastructure from Scratch",
                    "description": "Build mini cloud platform with compute, storage, networking",
                    "objectives": [
                        "VM orchestrator",
                        "Object storage system",
                        "Software-defined networking",
                        "API gateway",
                        "Auto-scaler with KPIs",
                        "Trust score system",
                        "Cost optimizer"
                    ],
                    "complexity": 10
                },
                {
                    "id": "proj_k8s_clone",
                    "name": "Kubernetes-like Orchestrator",
                    "description": "Build container orchestrator with scheduling",
                    "objectives": ["Scheduler", "Controller", "API server", "etcd-like store"],
                    "complexity": 9
                }
            ],
            prerequisites=["programming", "data_engineering"]
        )
        
        # Domain 4: DevOps, SRE & Observability
        self.domains["devops_sre"] = KnowledgeDomain(
            domain_id="devops_sre",
            name="DevOps, SRE & Observability",
            topics=[
                "CI/CD pipelines",
                "Configuration management",
                "Monitoring & alerting",
                "Incident response",
                "Chaos engineering",
                "Load balancing & failover",
                "Disaster recovery",
                "SRE principles (SLIs, SLOs, error budgets)"
            ],
            learning_projects=[
                {
                    "id": "proj_cicd_platform",
                    "name": "CI/CD Platform",
                    "description": "Build GitHub Actions-like CI/CD system",
                    "objectives": ["Pipeline engine", "Runners", "Artifacts", "Notifications"],
                    "complexity": 8
                },
                {
                    "id": "proj_observability_stack",
                    "name": "Observability Stack",
                    "description": "Build metrics, logs, traces collector and visualizer",
                    "objectives": ["Metrics scraper", "Log aggregator", "Trace collector", "Dashboards"],
                    "complexity": 8
                }
            ],
            prerequisites=["programming", "cloud_infrastructure"]
        )
        
        # Domain 5: Security & Compliance
        self.domains["security"] = KnowledgeDomain(
            domain_id="security",
            name="Security & Compliance",
            topics=[
                "Application security (OWASP)",
                "Identity & access management",
                "Cryptography",
                "Cloud security",
                "DevSecOps",
                "Compliance (SOC2, GDPR, HIPAA)",
                "Threat modeling",
                "Security automation"
            ],
            learning_projects=[
                {
                    "id": "proj_iam_system",
                    "name": "Identity & Access Management System",
                    "description": "Build OAuth/OIDC provider with RBAC",
                    "objectives": ["OAuth flow", "JWT tokens", "RBAC engine", "MFA"],
                    "complexity": 7
                },
                {
                    "id": "proj_secrets_vault",
                    "name": "Secrets Management Vault",
                    "description": "Build HashiCorp Vault-like system",
                    "objectives": ["Encryption", "Key rotation", "Access policies", "Audit log"],
                    "complexity": 8
                }
            ],
            prerequisites=["programming"]
        )
        
        # Domain 6: Software Architecture
        self.domains["architecture"] = KnowledgeDomain(
            domain_id="architecture",
            name="Software & System Architecture",
            topics=[
                "Architecture patterns (layered, microservices, event-driven)",
                "Distributed systems",
                "CAP theorem, consensus",
                "System design",
                "Enterprise architecture",
                "API design",
                "High availability",
                "Performance optimization"
            ],
            learning_projects=[
                {
                    "id": "proj_distributed_db",
                    "name": "Distributed Database",
                    "description": "Build Raft consensus-based distributed key-value store",
                    "objectives": ["Raft consensus", "Replication", "Sharding", "Consistency"],
                    "complexity": 10
                },
                {
                    "id": "proj_api_gateway",
                    "name": "API Gateway & Service Mesh",
                    "description": "Build routing, rate limiting, auth gateway",
                    "objectives": ["Routing", "Rate limiting", "Circuit breaker", "Observability"],
                    "complexity": 8
                }
            ],
            prerequisites=["programming", "cloud_infrastructure"]
        )
        
        # Domain 7: Machine Learning & AI
        self.domains["ml_ai"] = KnowledgeDomain(
            domain_id="ml_ai",
            name="Machine Learning, Deep Learning & AI",
            topics=[
                "Classical ML (regression, classification, clustering)",
                "Deep learning (CNNs, RNNs, Transformers)",
                "Reinforcement learning",
                "MLOps (experiment tracking, model registry)",
                "Generative AI (LLMs, diffusion models)",
                "RAG systems",
                "Model optimization",
                "AI ethics & bias"
            ],
            learning_projects=[
                {
                    "id": "proj_ml_framework",
                    "name": "ML Framework from Scratch",
                    "description": "Build PyTorch-like framework with autograd",
                    "objectives": ["Tensor ops", "Autograd", "Optimizers", "Layers", "GPU support"],
                    "complexity": 10
                },
                {
                    "id": "proj_llm_training",
                    "name": "Train Small Language Model",
                    "description": "Train transformer model from scratch",
                    "objectives": ["Tokenizer", "Transformer", "Training loop", "Inference"],
                    "complexity": 9
                },
                {
                    "id": "proj_rag_engine",
                    "name": "RAG System with Vector DB",
                    "description": "Build retrieval-augmented generation system",
                    "objectives": ["Embeddings", "Vector search", "Retrieval", "Generation"],
                    "complexity": 7
                }
            ],
            prerequisites=["programming", "data_engineering"]
        )
        
        # Domain 8: Business Applications (CRM - PRIORITY)
        self.domains["business_apps"] = KnowledgeDomain(
            domain_id="business_apps",
            name="Business Applications & Product",
            topics=[
                "CRM systems",
                "E-commerce platforms",
                "Payment processing",
                "Analytics & reporting",
                "Product management",
                "Growth & marketing automation",
                "Customer success platforms",
                "Business intelligence"
            ],
            learning_projects=[
                {
                    "id": "proj_crm_system",
                    "name": "Full CRM System",
                    "description": "Build Salesforce-like CRM from scratch",
                    "objectives": [
                        "Contact/account management",
                        "Sales pipeline",
                        "Email integration",
                        "Reporting dashboard",
                        "Automation workflows",
                        "Mobile API",
                        "Multi-tenancy"
                    ],
                    "complexity": 9
                },
                {
                    "id": "proj_ecommerce_tracking",
                    "name": "E-commerce API Ingestion & Market Prediction",
                    "description": "Build e-commerce analytics SaaS platform",
                    "objectives": [
                        "API integrations (Shopify, WooCommerce, etc)",
                        "Real-time data ingestion",
                        "Market trend prediction ML models",
                        "Ad funnel optimization",
                        "Customer behavior analytics",
                        "Revenue forecasting",
                        "Multi-tenant SaaS architecture"
                    ],
                    "complexity": 10
                }
            ],
            prerequisites=["programming", "data_engineering", "ml_ai"]
        )
        
        # Domain 9: Emerging Tech
        self.domains["emerging_tech"] = KnowledgeDomain(
            domain_id="emerging_tech",
            name="Emerging Technologies",
            topics=[
                "Blockchain & Web3",
                "Smart contracts",
                "DeFi protocols",
                "Edge computing",
                "IoT platforms",
                "Quantum computing",
                "AR/VR/XR",
                "Decentralized systems"
            ],
            learning_projects=[
                {
                    "id": "proj_blockchain",
                    "name": "Blockchain from Scratch",
                    "description": "Build Bitcoin-like blockchain with consensus",
                    "objectives": ["Block structure", "Proof of work", "P2P network", "Wallets"],
                    "complexity": 9
                },
                {
                    "id": "proj_smart_contract_platform",
                    "name": "Smart Contract Platform",
                    "description": "Build Ethereum-like smart contract platform",
                    "objectives": ["VM", "Contract language", "Gas metering", "State management"],
                    "complexity": 10
                }
            ],
            prerequisites=["programming", "architecture", "security"]
        )
        
        self.total_domains = len(self.domains)
        logger.info(f"[CURRICULUM] Initialized {self.total_domains} knowledge domains")
    
    def get_next_project(self) -> Optional[LearningProject]:
        """
        Get next project Grace should work on
        Prioritizes: CRM, E-commerce tracking, Cloud infrastructure
        """
        
        # Priority projects (business need + learning value)
        priority_projects = [
            "proj_crm_system",
            "proj_ecommerce_tracking",
            "proj_cloud_infra_scratch"
        ]
        
        # Check if priority projects are available
        for proj_id in priority_projects:
            for domain in self.domains.values():
                for proj_config in domain.learning_projects:
                    if proj_config['id'] == proj_id:
                        # Check prerequisites
                        if self._prerequisites_met(domain.prerequisites):
                            project = self._create_project(proj_config, domain.domain_id)
                            return project
        
        # Otherwise, pick next project based on prerequisites
        for domain in self.domains.values():
            if self._prerequisites_met(domain.prerequisites):
                for proj_config in domain.learning_projects:
                    if proj_config['id'] not in [p.project_id for p in self.projects.values() if p.status == "completed"]:
                        project = self._create_project(proj_config, domain.domain_id)
                        return project
        
        return None
    
    def _create_project(self, config: Dict[str, Any], domain: str) -> LearningProject:
        """Create project from config"""
        project = LearningProject(
            project_id=config['id'],
            name=config['name'],
            description=config['description'],
            domain=domain,
            objectives=config['objectives'],
            success_criteria={
                'min_trust_score': 70.0,
                'all_objectives_met': True,
                'tests_passing': True,
                'documented': True
            },
            estimated_complexity=config['complexity']
        )
        return project
    
    def _prerequisites_met(self, prerequisites: List[str]) -> bool:
        """Check if prerequisites are met"""
        for prereq in prerequisites:
            if prereq not in self.domains:
                return False
            if self.domains[prereq].mastery_level < 60.0:  # 60% threshold
                return False
        return True
    
    def start_project(self, project: LearningProject) -> Dict[str, Any]:
        """Start working on a project"""
        project.status = "in_progress"
        project.started_at = datetime.utcnow().isoformat()
        
        self.projects[project.project_id] = project
        self.current_focus = project.project_id
        
        self._save_progress()
        
        logger.info(f"[CURRICULUM] Started project: {project.name}")
        logger.info(f"[CURRICULUM] Domain: {project.domain}")
        logger.info(f"[CURRICULUM] Objectives: {', '.join(project.objectives)}")
        
        return {
            'project_id': project.project_id,
            'name': project.name,
            'objectives': project.objectives,
            'started_at': project.started_at
        }
    
    def complete_project(
        self,
        project_id: str,
        trust_score: float,
        kpis: Dict[str, float],
        learnings: List[str]
    ) -> Dict[str, Any]:
        """Mark project as complete"""
        if project_id not in self.projects:
            return {'error': 'project_not_found'}
        
        project = self.projects[project_id]
        project.status = "completed"
        project.completed_at = datetime.utcnow().isoformat()
        project.trust_score = trust_score
        project.kpis = kpis
        project.learnings = learnings
        
        # Update domain mastery
        domain = self.domains[project.domain]
        domain.projects_completed.append(project_id)
        domain.skills_acquired.extend(project.objectives)
        
        # Calculate new mastery level
        total_projects = len(domain.learning_projects)
        completed_projects = len(domain.projects_completed)
        domain.mastery_level = (completed_projects / total_projects) * 100
        
        # Update global stats
        self.projects_completed += 1
        if domain.mastery_level >= 80.0:
            self.domains_mastered += 1
        
        self._save_progress()
        
        logger.info(f"[CURRICULUM] ✅ Completed: {project.name}")
        logger.info(f"[CURRICULUM] Trust score: {trust_score}")
        logger.info(f"[CURRICULUM] Domain mastery: {domain.mastery_level:.1f}%")
        
        return {
            'project_id': project_id,
            'trust_score': trust_score,
            'domain_mastery': domain.mastery_level,
            'learnings_count': len(learnings)
        }
    
    def get_progress_report(self) -> Dict[str, Any]:
        """Get complete learning progress"""
        return {
            'total_domains': self.total_domains,
            'domains_mastered': self.domains_mastered,
            'projects_completed': self.projects_completed,
            'current_focus': self.current_focus,
            'domains': {
                domain_id: {
                    'name': domain.name,
                    'mastery_level': domain.mastery_level,
                    'projects_completed': len(domain.projects_completed),
                    'total_projects': len(domain.learning_projects)
                }
                for domain_id, domain in self.domains.items()
            }
        }
    
    def _save_progress(self):
        """Save learning progress"""
        progress = {
            'domains_mastered': self.domains_mastered,
            'projects_completed': self.projects_completed,
            'current_focus': self.current_focus,
            'total_learning_hours': self.total_learning_hours,
            'projects': {
                proj_id: {
                    'project_id': proj.project_id,
                    'name': proj.name,
                    'status': proj.status,
                    'trust_score': proj.trust_score,
                    'kpis': proj.kpis,
                    'started_at': proj.started_at,
                    'completed_at': proj.completed_at
                }
                for proj_id, proj in self.projects.items()
            },
            'domain_mastery': {
                domain_id: domain.mastery_level
                for domain_id, domain in self.domains.items()
            }
        }
        
        progress_file = self.storage_path / "learning_progress.json"
        progress_file.write_text(json.dumps(progress, indent=2))
    
    def _load_progress(self):
        """Load learning progress"""
        progress_file = self.storage_path / "learning_progress.json"
        if not progress_file.exists():
            return
        
        try:
            progress = json.loads(progress_file.read_text())
            self.domains_mastered = progress.get('domains_mastered', 0)
            self.projects_completed = progress.get('projects_completed', 0)
            self.current_focus = progress.get('current_focus')
            self.total_learning_hours = progress.get('total_learning_hours', 0)
            
            # Restore domain mastery
            for domain_id, mastery in progress.get('domain_mastery', {}).items():
                if domain_id in self.domains:
                    self.domains[domain_id].mastery_level = mastery
            
            logger.info(f"[CURRICULUM] Loaded progress: {self.projects_completed} projects completed")
        except Exception as e:
            logger.error(f"[CURRICULUM] Failed to load progress: {e}")


# Global instance
autonomous_curriculum = AutonomousCurriculum()
