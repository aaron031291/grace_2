import hashlib
import json
from typing import Optional, List
from sqlalchemy import select
from .memory_models import MemoryArtifact, MemoryOperation, MemoryEvent
from .models import async_session
from datetime import datetime

class MemoryService:
    """Unified memory management with immutable audit trail"""
    
    @staticmethod
    def _compute_content_hash(content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def create_artifact(
        self,
        path: str,
        content: str,
        actor: str,
        domain: str = "general",
        category: str = "knowledge",
        metadata: dict = None,
        reason: str = ""
    ) -> int:
        """Create new memory artifact with audit trail"""
        
        content_hash = self._compute_content_hash(content)
        
        async with async_session() as session:
            artifact = MemoryArtifact(
                path=path,
                content=content,
                content_hash=content_hash,
                artifact_metadata=json.dumps(metadata or {}),
                domain=domain,
                category=category,
                created_by=actor,
                status="draft"
            )
            session.add(artifact)
            await session.flush()
            
            operation_hash = MemoryOperation.compute_hash(
                artifact.id, "create", actor, content_hash, ""
            )
            
            operation = MemoryOperation(
                artifact_id=artifact.id,
                operation="create",
                actor=actor,
                previous_content_hash="",
                new_content_hash=content_hash,
                operation_hash=operation_hash,
                previous_operation_hash="",
                reason=reason,
                metadata=json.dumps({"domain": domain, "category": category})
            )
            session.add(operation)
            
            event = MemoryEvent(
                event_type="memory.item.created",
                artifact_id=artifact.id,
                artifact_path=path,
                actor=actor,
                payload=json.dumps({"domain": domain, "category": category})
            )
            session.add(event)
            
            await session.commit()
            
            print(f"✓ Memory created: {path} by {actor}")
            
            from .trigger_mesh import trigger_mesh, TriggerEvent
            from datetime import datetime as dt
            await trigger_mesh.publish(TriggerEvent(
                event_type="memory.item.created",
                source="memory_service",
                actor=actor,
                resource=path,
                payload={"domain": domain, "category": category, "artifact_id": artifact.id},
                timestamp=dt.utcnow()
            ))
            
            return artifact.id
    
    async def update_artifact(
        self,
        artifact_id: int,
        content: str,
        actor: str,
        reason: str = ""
    ) -> bool:
        """Update artifact with audit trail"""
        
        new_hash = self._compute_content_hash(content)
        
        async with async_session() as session:
            artifact = await session.get(MemoryArtifact, artifact_id)
            if not artifact:
                return False
            
            prev_result = await session.execute(
                select(MemoryOperation)
                .where(MemoryOperation.artifact_id == artifact_id)
                .order_by(MemoryOperation.timestamp.desc())
                .limit(1)
            )
            last_operation = prev_result.scalar_one_or_none()
            prev_op_hash = last_operation.operation_hash if last_operation else ""
            
            old_hash = artifact.content_hash
            artifact.content = content
            artifact.content_hash = new_hash
            artifact.version += 1
            
            operation_hash = MemoryOperation.compute_hash(
                artifact_id, "update", actor, new_hash, prev_op_hash
            )
            
            operation = MemoryOperation(
                artifact_id=artifact_id,
                operation="update",
                actor=actor,
                previous_content_hash=old_hash,
                new_content_hash=new_hash,
                operation_hash=operation_hash,
                previous_operation_hash=prev_op_hash,
                reason=reason
            )
            session.add(operation)
            
            event = MemoryEvent(
                event_type="memory.item.updated",
                artifact_id=artifact_id,
                artifact_path=artifact.path,
                actor=actor,
                payload=json.dumps({"old_hash": old_hash, "new_hash": new_hash})
            )
            session.add(event)
            
            await session.commit()
            
            print(f"✓ Memory updated: {artifact.path} (v{artifact.version}) by {actor}")
            
            from .trigger_mesh import trigger_mesh, TriggerEvent
            from datetime import datetime as dt
            await trigger_mesh.publish(TriggerEvent(
                event_type="memory.item.updated",
                source="memory_service",
                actor=actor,
                resource=artifact.path,
                payload={"artifact_id": artifact_id, "version": artifact.version},
                timestamp=dt.utcnow()
            ))
            
            return True
    
    async def get_artifact(self, path: str) -> Optional[dict]:
        """Retrieve artifact by path"""
        async with async_session() as session:
            result = await session.execute(
                select(MemoryArtifact).where(
                    MemoryArtifact.path == path,
                    MemoryArtifact.is_deleted == False
                )
            )
            artifact = result.scalar_one_or_none()
            if artifact:
                return {
                    "id": artifact.id,
                    "path": artifact.path,
                    "content": artifact.content,
                    "domain": artifact.domain,
                    "category": artifact.category,
                    "status": artifact.status,
                    "version": artifact.version,
                    "created_by": artifact.created_by,
                    "created_at": artifact.created_at,
                    "updated_at": artifact.updated_at
                }
        return None
    
    async def list_artifacts(
        self,
        domain: str = None,
        category: str = None,
        status: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """List artifacts with optional filters and pagination"""
        async with async_session() as session:
            query = select(MemoryArtifact).where(MemoryArtifact.is_deleted == False)
            if domain:
                query = query.where(MemoryArtifact.domain == domain)
            if category:
                query = query.where(MemoryArtifact.category == category)
            if status:
                query = query.where(MemoryArtifact.status == status)
            
            query = query.order_by(MemoryArtifact.path).limit(limit).offset(offset)
            result = await session.execute(query)
            return [
                {
                    "id": a.id,
                    "path": a.path,
                    "domain": a.domain,
                    "category": a.category,
                    "status": a.status,
                    "version": a.version,
                    "size": len(a.content),
                    "created_by": a.created_by,
                    "updated_at": a.updated_at
                }
                for a in result.scalars()
            ]
    
    async def get_audit_trail(self, artifact_id: int, limit: int = 1000) -> List[dict]:
        """Get complete audit history for an artifact"""
        async with async_session() as session:
            result = await session.execute(
                select(MemoryOperation)
                .where(MemoryOperation.artifact_id == artifact_id)
                .order_by(MemoryOperation.timestamp.desc())
                .limit(limit)
            )
            return [
                {
                    "operation": op.operation,
                    "actor": op.actor,
                    "reason": op.reason,
                    "operation_hash": op.operation_hash,
                    "previous_hash": op.previous_operation_hash,
                    "timestamp": op.timestamp
                }
                for op in result.scalars()
            ]
    
    async def verify_chain(self, artifact_id: int, max_operations: int = 10000) -> dict:
        """Verify hash chain integrity"""
        async with async_session() as session:
            result = await session.execute(
                select(MemoryOperation)
                .where(MemoryOperation.artifact_id == artifact_id)
                .order_by(MemoryOperation.timestamp.asc())
                .limit(max_operations)
            )
            operations = list(result.scalars())
            
            for i, op in enumerate(operations):
                if i > 0:
                    expected_prev = operations[i-1].operation_hash
                    if op.previous_operation_hash != expected_prev:
                        return {
                            "valid": False,
                            "broken_at": i,
                            "message": f"Chain broken at operation {op.id}"
                        }
            
            return {"valid": True, "operations_verified": len(operations)}

memory_service = MemoryService()
