"""
Synthetic Q/A Benchmark Generator - 100+ pairs
"""
import json
import asyncio
from typing import List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SyntheticQABenchmarkGenerator:
    """Generate synthetic Q/A benchmark dataset"""
    
    def __init__(self):
        self.benchmark_data = []
        self.categories = [
            "system_operations", "troubleshooting", "configuration", 
            "security", "performance", "monitoring", "deployment"
        ]
    
    async def generate_benchmark_dataset(self, target_size: int = 150) -> List[Dict]:
        """Generate comprehensive Q/A benchmark dataset"""
        print(f"🔄 Generating {target_size} Q/A pairs...")
        
        # Generate questions by category
        questions_per_category = target_size // len(self.categories)
        
        for category in self.categories:
            category_questions = await self._generate_category_questions(
                category, questions_per_category
            )
            self.benchmark_data.extend(category_questions)
        
        # Add edge cases and hard negatives
        edge_cases = await self._generate_edge_cases(20)
        self.benchmark_data.extend(edge_cases)
        
        # Shuffle and assign IDs
        import random
        random.shuffle(self.benchmark_data)
        
        for i, item in enumerate(self.benchmark_data):
            item["qa_id"] = f"qa_{i+1:03d}"
            item["created_at"] = datetime.utcnow().isoformat()
        
        print(f"✅ Generated {len(self.benchmark_data)} Q/A pairs")
        return self.benchmark_data
    
    async def _generate_category_questions(self, category: str, count: int) -> List[Dict]:
        """Generate questions for specific category"""
        templates = self._get_category_templates(category)
        questions = []
        
        for i in range(count):
            template = templates[i % len(templates)]
            qa_pair = {
                "question": template["question"],
                "expected_answer": template["answer"],
                "category": category,
                "difficulty": template.get("difficulty", "medium"),
                "expected_sources": template.get("sources", []),
                "keywords": template.get("keywords", []),
                "answer_type": template.get("type", "factual")
            }
            questions.append(qa_pair)
        
        return questions
    
    def _get_category_templates(self, category: str) -> List[Dict]:
        """Get question templates by category"""
        templates = {
            "system_operations": [
                {
                    "question": "How do I restart a failed service?",
                    "answer": "Use systemctl restart <service-name> or the service restart playbook",
                    "sources": ["playbooks/service_restart.yaml"],
                    "keywords": ["restart", "service", "systemctl"],
                    "difficulty": "easy"
                },
                {
                    "question": "What is the MTTR target for critical incidents?",
                    "answer": "MTTR target is 5 minutes for critical incidents",
                    "sources": ["docs/sla.md"],
                    "keywords": ["MTTR", "critical", "target"],
                    "difficulty": "medium"
                },
                {
                    "question": "How do I check system resource usage?",
                    "answer": "Use top, htop, or the monitoring dashboard to check CPU, memory, and disk usage",
                    "sources": ["docs/monitoring.md"],
                    "keywords": ["resources", "monitoring", "CPU", "memory"],
                    "difficulty": "easy"
                }
            ],
            "troubleshooting": [
                {
                    "question": "Service is not responding, what should I check first?",
                    "answer": "Check if the service is running, review logs, verify network connectivity",
                    "sources": ["playbooks/troubleshooting.yaml"],
                    "keywords": ["troubleshooting", "service", "logs"],
                    "difficulty": "medium"
                },
                {
                    "question": "Database connection timeout, how to diagnose?",
                    "answer": "Check connection pool, database server status, network latency, and query performance",
                    "sources": ["docs/database_troubleshooting.md"],
                    "keywords": ["database", "timeout", "connection"],
                    "difficulty": "hard"
                }
            ],
            "security": [
                {
                    "question": "How do I rotate API keys?",
                    "answer": "Use the key rotation playbook: generate new key, update services, revoke old key",
                    "sources": ["playbooks/key_rotation.yaml"],
                    "keywords": ["API", "keys", "rotation", "security"],
                    "difficulty": "medium"
                },
                {
                    "question": "What should I do if I detect unauthorized access?",
                    "answer": "Immediately revoke access, change credentials, review audit logs, notify security team",
                    "sources": ["docs/incident_response.md"],
                    "keywords": ["unauthorized", "access", "security", "incident"],
                    "difficulty": "hard"
                }
            ],
            "performance": [
                {
                    "question": "How do I optimize slow database queries?",
                    "answer": "Add indexes, optimize query structure, check execution plans, consider caching",
                    "sources": ["docs/performance_tuning.md"],
                    "keywords": ["performance", "database", "queries", "optimization"],
                    "difficulty": "hard"
                }
            ],
            "monitoring": [
                {
                    "question": "How do I set up alerts for high CPU usage?",
                    "answer": "Configure monitoring thresholds and alert rules in the monitoring system",
                    "sources": ["docs/alerting.md"],
                    "keywords": ["alerts", "CPU", "monitoring", "thresholds"],
                    "difficulty": "medium"
                }
            ],
            "deployment": [
                {
                    "question": "How do I rollback a failed deployment?",
                    "answer": "Use the rollback playbook to revert to the previous stable version",
                    "sources": ["playbooks/rollback.yaml"],
                    "keywords": ["rollback", "deployment", "revert"],
                    "difficulty": "medium"
                }
            ]
        }
        
        return templates.get(category, [])
    
    async def _generate_edge_cases(self, count: int) -> List[Dict]:
        """Generate edge cases and hard negatives"""
        edge_cases = [
            {
                "question": "What is the meaning of life?",
                "expected_answer": "This question is outside the scope of system operations",
                "category": "edge_case",
                "difficulty": "hard",
                "answer_type": "out_of_scope"
            },
            {
                "question": "How do I cook pasta?",
                "expected_answer": "This is not related to system operations or IT infrastructure",
                "category": "edge_case", 
                "difficulty": "hard",
                "answer_type": "out_of_scope"
            },
            {
                "question": "",
                "expected_answer": "Empty question - no answer can be provided",
                "category": "edge_case",
                "difficulty": "hard",
                "answer_type": "invalid_input"
            },
            {
                "question": "asdfghjkl qwertyuiop",
                "expected_answer": "Gibberish input - no meaningful answer available",
                "category": "edge_case",
                "difficulty": "hard", 
                "answer_type": "invalid_input"
            }
        ]
        
        # Repeat edge cases to reach target count
        while len(edge_cases) < count:
            edge_cases.extend(edge_cases[:min(len(edge_cases), count - len(edge_cases))])
        
        return edge_cases[:count]
    
    async def save_benchmark(self, filepath: str = "config/qa_benchmark.json"):
        """Save benchmark dataset to file"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump({
                "version": "1.0",
                "created_at": datetime.utcnow().isoformat(),
                "total_questions": len(self.benchmark_data),
                "categories": self.categories,
                "questions": self.benchmark_data
            }, f, indent=2)
        
        print(f"💾 Benchmark saved to {filepath}")
        return filepath

# Global instance
qa_benchmark_generator = SyntheticQABenchmarkGenerator()
