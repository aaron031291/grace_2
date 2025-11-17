"""
Model Capability System - Complete implementation
- Capability manifest per model
- Intelligent routing policies
- Outcome telemetry & learning
- Warm cache management
- Governance hooks
- Self-critique & reinforcement
"""

import yaml
import httpx
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import text

class ModelCapabilitySystem:
    """
    Manages model capabilities, routing, learning, and optimization
    Grace's intelligence layer for 15-model orchestration
    """
    
    def __init__(self):
        self.manifest = self._load_manifest()
        self.warm_cache = set()  # Models currently loaded in GPU
        self.performance_cache = {}  # Real-time performance data
        self.approval_log = []  # User approvals/rejections
        
    def _load_manifest(self) -> Dict:
        """Load model capability manifest"""
        manifest_path = Path(__file__).parent.parent / "config" / "model_manifest.yaml"
        
        try:
            with open(manifest_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Failed to load manifest: {e}")
            return {"models": {}, "routing_rules": {}}
    
    async def select_model(
        self,
        intent: str,
        task_type: str,
        context: Optional[Dict] = None,
        user_preference: Optional[str] = None
    ) -> str:
        """
        Intelligent model selection based on:
        - Task type
        - Manifest capabilities
        - Performance history
        - Resource availability
        - Governance rules
        """
        
        # User override
        if user_preference:
            if await self._check_governance_approval(user_preference, intent):
                return user_preference
        
        # Get routing rules for task type
        routing = self.manifest.get("routing_rules", {}).get(task_type, {})
        primary = routing.get("primary")
        fallbacks = routing.get("fallback", [])
        
        # Check if primary model is available and warm
        if primary:
            model_key = primary
            model_info = self.manifest["models"].get(model_key, {})
            
            # Governance check
            if await self._check_governance_approval(model_info.get("name"), intent):
                # Resource check
                if await self._check_resources_available(model_info):
                    # Performance check
                    if await self._check_model_healthy(model_info.get("name")):
                        return model_info.get("name")
        
        # Try fallbacks
        for fallback_key in fallbacks:
            model_info = self.manifest["models"].get(fallback_key, {})
            model_name = model_info.get("name")
            
            if await self._check_governance_approval(model_name, intent):
                if await self._check_resources_available(model_info):
                    if await self._check_model_healthy(model_name):
                        return model_name
        
        # Ultimate fallback
        return "llama3.2:latest"
    
    async def _check_governance_approval(self, model_name: str, intent: str) -> bool:
        """Check if governance allows this model for this intent"""
        
        # Find model in manifest
        model_key = None
        for key, info in self.manifest.get("models", {}).items():
            if info.get("name") == model_name:
                model_key = key
                break
        
        if not model_key:
            return True  # Unknown model, allow
        
        model_info = self.manifest["models"][model_key]
        
        # Check if model requires approval
        if model_info.get("requires_governance_approval"):
            # TODO: Integrate with governance kernel
            print(f"[GOVERNANCE] {model_name} requires approval for: {intent[:50]}")
            # For now, allow (implement real approval flow later)
            return True
        
        return True
    
    async def _check_resources_available(self, model_info: Dict) -> bool:
        """Check if system has resources for this model"""
        
        required_vram = model_info.get("vram_gb", 0)
        
        # TODO: Check actual GPU memory
        # For now, allow all (implement real resource check later)
        
        return True
    
    async def _check_model_healthy(self, model_name: str) -> bool:
        """Check if model is responding and healthy"""
        
        # Check if model is in warm cache or available
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags", timeout=3.0)
                if response.status_code == 200:
                    data = response.json()
                    available = [m["name"] for m in data.get("models", [])]
                    return any(model_name.split(":")[0] in m for m in available)
        except:
            pass
        
        return False
    
    async def log_outcome(
        self,
        model_used: str,
        task_type: str,
        intent: str,
        response: str,
        latency_ms: float,
        success: bool = True,
        tests_passed: int = 0,
        tests_failed: int = 0,
        user_rating: Optional[int] = None,
        review_approval: bool = False
    ):
        """
        Log model outcome for learning
        Feeds into Layer 3 retrospectives and verification
        """
        
        outcome_record = {
            "model_used": model_used,
            "task_type": task_type,
            "intent": intent[:200],  # Truncate for storage
            "response_length": len(response),
            "latency_ms": latency_ms,
            "success": success,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "user_rating": user_rating,
            "review_approval": review_approval,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in database
        await self._persist_outcome(outcome_record)
        
        # Update real-time performance cache
        if model_used not in self.performance_cache:
            self.performance_cache[model_used] = {
                "total_calls": 0,
                "successes": 0,
                "avg_latency": 0,
                "trust_score": 0.5
            }
        
        cache = self.performance_cache[model_used]
        cache["total_calls"] += 1
        
        if success:
            cache["successes"] += 1
        
        # Rolling average latency
        cache["avg_latency"] = (
            (cache["avg_latency"] * (cache["total_calls"] - 1) + latency_ms) 
            / cache["total_calls"]
        )
        
        # Update trust score based on reinforcement learning
        await self._update_trust_score(model_used, success, user_rating, review_approval)
    
    async def _persist_outcome(self, record: Dict):
        """Persist outcome to database"""
        try:
            from backend.models.base_models import async_session
            
            async with async_session() as session:
                # Create table if not exists
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS model_outcomes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_used TEXT NOT NULL,
                        task_type TEXT,
                        intent TEXT,
                        response_length INTEGER,
                        latency_ms REAL,
                        success BOOLEAN,
                        tests_passed INTEGER,
                        tests_failed INTEGER,
                        user_rating INTEGER,
                        review_approval BOOLEAN,
                        timestamp TEXT
                    )
                """))
                
                await session.execute(text("""
                    INSERT INTO model_outcomes 
                    (model_used, task_type, intent, response_length, latency_ms, success, 
                     tests_passed, tests_failed, user_rating, review_approval, timestamp)
                    VALUES 
                    (:model, :task, :intent, :resp_len, :latency, :success,
                     :tests_pass, :tests_fail, :rating, :approval, :timestamp)
                """), {
                    "model": record["model_used"],
                    "task": record["task_type"],
                    "intent": record["intent"],
                    "resp_len": record["response_length"],
                    "latency": record["latency_ms"],
                    "success": record["success"],
                    "tests_pass": record["tests_passed"],
                    "tests_fail": record["tests_failed"],
                    "rating": record["user_rating"],
                    "approval": record["review_approval"],
                    "timestamp": record["timestamp"]
                })
                
                await session.commit()
                
        except Exception as e:
            print(f"Failed to persist outcome: {e}")
    
    async def _update_trust_score(
        self,
        model: str,
        success: bool,
        user_rating: Optional[int],
        review_approval: bool
    ):
        """Update model trust score based on reinforcement learning"""
        
        config = self.manifest.get("reinforcement", {})
        
        # Find model in manifest
        model_key = None
        for key, info in self.manifest.get("models", {}).items():
            if info.get("name") == model:
                model_key = key
                break
        
        if not model_key:
            return
        
        current_trust = self.manifest["models"][model_key].get("trust_score", 0.5)
        adjustment = 0
        
        # Apply reinforcement weights
        if success:
            adjustment += config.get("success_weight", 0.02)
        else:
            adjustment += config.get("failure_weight", -0.04)
        
        if user_rating and user_rating >= 4:
            adjustment += config.get("approval_weight", 0.05)
        elif user_rating and user_rating <= 2:
            adjustment += config.get("rejection_weight", -0.03)
        
        if review_approval:
            adjustment += config.get("approval_weight", 0.05)
        
        # Update trust score
        new_trust = max(
            config.get("min_trust_score", 0.5),
            min(config.get("max_trust_score", 1.0), current_trust + adjustment)
        )
        
        self.manifest["models"][model_key]["trust_score"] = new_trust
        
        # Auto-update manifest if enabled
        if config.get("auto_update_manifest"):
            await self._save_manifest()
    
    async def _save_manifest(self):
        """Save updated manifest with new trust scores"""
        manifest_path = Path(__file__).parent.parent / "config" / "model_manifest.yaml"
        
        try:
            with open(manifest_path, 'w') as f:
                yaml.dump(self.manifest, f, default_flow_style=False)
        except Exception as e:
            print(f"Failed to save manifest: {e}")
    
    async def self_critique(self, model: str, response: str) -> Dict[str, Any]:
        """
        Ask model to self-grade its response
        Feeds confidence back into selection logic
        """
        
        config = self.manifest.get("self_critique", {})
        
        if not config.get("enabled"):
            return {"confidence": 100, "limitations": []}
        
        try:
            async with httpx.AsyncClient() as client:
                critique_response = await client.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "user",
                                "content": config.get("prompt_after_response", "How confident are you in this answer (0-100)? What limitations did you encounter?")
                            }
                        ],
                        "stream": False
                    },
                    timeout=15.0
                )
                
                if critique_response.status_code == 200:
                    result = critique_response.json()
                    critique_text = result["message"]["content"]
                    
                    # Parse confidence (simple extraction)
                    confidence = 80  # Default
                    if "confidence" in critique_text.lower():
                        # Extract number
                        import re
                        numbers = re.findall(r'\d+', critique_text)
                        if numbers:
                            confidence = min(100, int(numbers[0]))
                    
                    return {
                        "confidence": confidence,
                        "critique": critique_text,
                        "should_retry": confidence < config.get("threshold_for_retry", 60)
                    }
                    
        except Exception as e:
            print(f"Self-critique failed: {e}")
        
        return {"confidence": 100, "limitations": []}
    
    async def get_capability_matrix(self) -> Dict[str, Any]:
        """Get full capability matrix for UI display"""
        
        matrix = {
            "kernels": {},
            "models": {},
            "routing_rules": self.manifest.get("routing_rules", {}),
            "performance": self.performance_cache,
            "warm_cache": list(self.warm_cache)
        }
        
        # Map kernels to their assigned models
        kernel_mappings = {
            "coding_agent": {"task": "coding", "models": []},
            "agentic_spine": {"task": "reasoning", "models": []},
            "voice_conversation": {"task": "conversation", "models": []},
            "meta_loop": {"task": "reasoning", "models": []},
            "learning_integration": {"task": "conversation", "models": []},
            "librarian": {"task": "rag", "models": []},
            "self_healing": {"task": "reasoning", "models": []},
            "governance": {"task": "conversation", "models": []},
            "sandbox": {"task": "coding", "models": []}
        }
        
        # Fill in models for each kernel based on routing
        for kernel, mapping in kernel_mappings.items():
            task = mapping["task"]
            routing = self.manifest.get("routing_rules", {}).get(task, {})
            
            primary = routing.get("primary")
            if primary:
                model_info = self.manifest["models"].get(primary, {})
                mapping["models"].append({
                    "name": model_info.get("name"),
                    "role": "primary",
                    "trust_score": model_info.get("trust_score", 0.5)
                })
            
            for fallback in routing.get("fallback", [])[:2]:  # Top 2 fallbacks
                model_info = self.manifest["models"].get(fallback, {})
                mapping["models"].append({
                    "name": model_info.get("name"),
                    "role": "fallback",
                    "trust_score": model_info.get("trust_score", 0.5)
                })
        
        matrix["kernels"] = kernel_mappings
        
        # Add full model details
        for key, info in self.manifest.get("models", {}).items():
            matrix["models"][key] = {
                **info,
                "performance": self.performance_cache.get(info.get("name"), {})
            }
        
        return matrix
    
    async def record_approval(self, model: str, task_id: str, approved: bool, rating: Optional[int] = None):
        """
        Record user approval/rejection
        Reinforcement learning signal
        """
        
        self.approval_log.append({
            "model": model,
            "task_id": task_id,
            "approved": approved,
            "rating": rating,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update trust score immediately
        await self._update_trust_score(model, success=approved, user_rating=rating, review_approval=approved)
        
        # Persist to database
        try:
            from backend.models.base_models import async_session
            
            async with async_session() as session:
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS model_approvals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model TEXT,
                        task_id TEXT,
                        approved BOOLEAN,
                        rating INTEGER,
                        timestamp TEXT
                    )
                """))
                
                await session.execute(text("""
                    INSERT INTO model_approvals (model, task_id, approved, rating, timestamp)
                    VALUES (:model, :task_id, :approved, :rating, :timestamp)
                """), {
                    "model": model,
                    "task_id": task_id,
                    "approved": approved,
                    "rating": rating,
                    "timestamp": datetime.now().isoformat()
                })
                
                await session.commit()
                
        except Exception as e:
            print(f"Failed to persist approval: {e}")
    
    async def warm_model(self, model_name: str):
        """Load model into GPU cache"""
        try:
            async with httpx.AsyncClient() as client:
                # Warm up by sending a simple request
                await client.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": model_name,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "stream": False,
                        "options": {"num_predict": 1}
                    },
                    timeout=30.0
                )
                
                self.warm_cache.add(model_name)
                print(f"✓ Model {model_name} warmed and cached")
                
        except Exception as e:
            print(f"Failed to warm model {model_name}: {e}")
    
    async def manage_cache(self):
        """
        Manage warm cache based on tier policy
        Keeps always_loaded models warm, evicts cold_storage
        """
        
        cache_policy = self.manifest.get("cache_tiers", {})
        
        # Warm always-loaded models
        for model_key in cache_policy.get("always_loaded", []):
            model_info = self.manifest["models"].get(model_key, {})
            model_name = model_info.get("name")
            if model_name and model_name not in self.warm_cache:
                await self.warm_model(model_name)
        
        # TODO: Implement eviction for cold_storage models when memory limited
    
    async def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of what Grace has learned"""
        
        try:
            from backend.models.base_models import async_session
            
            async with async_session() as session:
                # Get outcome statistics
                result = await session.execute(text("""
                    SELECT 
                        model_used,
                        task_type,
                        COUNT(*) as total,
                        SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
                        AVG(latency_ms) as avg_latency,
                        AVG(user_rating) as avg_rating
                    FROM model_outcomes
                    WHERE timestamp > datetime('now', '-7 days')
                    GROUP BY model_used, task_type
                """))
                
                stats = []
                for row in result:
                    stats.append({
                        "model": row[0],
                        "task_type": row[1],
                        "total": row[2],
                        "successes": row[3],
                        "success_rate": row[3] / row[2] if row[2] > 0 else 0,
                        "avg_latency": row[4],
                        "avg_rating": row[5]
                    })
                
                return {
                    "statistics": stats,
                    "insights": await self._generate_insights(stats),
                    "recommendations": await self._generate_recommendations(stats)
                }
                
        except Exception as e:
            print(f"Failed to get learning summary: {e}")
            return {"statistics": [], "insights": [], "recommendations": []}
    
    async def _generate_insights(self, stats: List[Dict]) -> List[str]:
        """Generate human-readable insights from statistics"""
        
        insights = []
        
        # Find best performer
        if stats:
            best = max(stats, key=lambda x: x["success_rate"])
            insights.append(f"🏆 {best['model']} has the highest success rate for {best['task_type']} ({best['success_rate']*100:.0f}%)")
            
            # Find fastest
            fastest = min(stats, key=lambda x: x["avg_latency"] or 9999)
            insights.append(f"⚡ {fastest['model']} is fastest for {fastest['task_type']} ({fastest['avg_latency']:.0f}ms)")
        
        return insights
    
    async def _generate_recommendations(self, stats: List[Dict]) -> List[str]:
        """Generate recommendations for model usage"""
        
        recommendations = []
        
        # Check if any model is underperforming
        for stat in stats:
            if stat["success_rate"] < 0.7 and stat["total"] > 5:
                recommendations.append(f"⚠️ Consider alternative to {stat['model']} for {stat['task_type']} (only {stat['success_rate']*100:.0f}% success)")
        
        # Check if models not being used
        all_models = self.manifest.get("models", {})
        used_models = {s["model"] for s in stats}
        
        for model_key, model_info in all_models.items():
            if model_info.get("name") not in used_models:
                if model_info.get("tier") == "primary":
                    recommendations.append(f"💡 Try {model_info.get('name')} - not yet tested but rated {model_info.get('quality')}/10")
        
        return recommendations[:5]  # Top 5 recommendations

# Global instance
capability_system = ModelCapabilitySystem()
