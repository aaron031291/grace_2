#!/usr/bin/env python3
"""
Learning Integration
Connects Memory Tables to ingestion pipelines and learning systems
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryTablesLearningBridge:
    """
    Bridges Memory Tables with ingestion pipelines and learning systems
    Ensures data flows: Tables → Ingestion → Learning → Insights
    """
    
    def __init__(self, registry=None):
        self.registry = registry
        self._learning_tasks = []
    
    async def sync_to_ingestion(self, table_name: str, row_id: str) -> bool:
        """
        Sync a table row to the ingestion pipeline
        Makes the data available for learning systems
        """
        try:
            # Get row data
            if not self.registry:
                from backend.memory_tables.registry import table_registry
                self.registry = table_registry
            
            model = self.registry.get_model(table_name)
            if not model:
                logger.error(f"Table not found: {table_name}")
                return False
            
            # Query the row
            from sqlmodel import Session, select
            import uuid
            
            with Session(self.registry.engine) as session:
                stmt = select(model).where(model.id == uuid.UUID(row_id))
                row = session.exec(stmt).first()
                
                if not row:
                    logger.error(f"Row not found: {row_id}")
                    return False
                
                # Convert row to dict
                row_data = {
                    k: str(v) if isinstance(v, uuid.UUID) else v
                    for k, v in row.__dict__.items()
                    if not k.startswith('_')
                }
            
            # Send to ingestion pipeline
            await self._send_to_ingestion_pipeline(table_name, row_data)
            
            # Update sync timestamp
            self.registry.update_row(table_name, uuid.UUID(row_id), {
                'last_synced_at': datetime.now()
            })
            
            logger.info(f"✅ Synced {table_name}/{row_id} to ingestion")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync to ingestion: {e}")
            return False
    
    async def _send_to_ingestion_pipeline(self, table_name: str, row_data: Dict[str, Any]):
        """Send data to the ingestion pipeline"""
        try:
            # Try to use existing ingestion routes
            from backend.routes import ingestion_api
            
            # Create ingestion job
            job_data = {
                'source': f"memory_tables/{table_name}",
                'data': row_data,
                'timestamp': datetime.now().isoformat()
            }
            
            # TODO: Actually call ingestion API when available
            logger.debug(f"Ingestion job created: {job_data}")
            
        except Exception as e:
            logger.warning(f"Ingestion pipeline not available: {e}")
    
    async def extract_insights(self, table_name: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Extract insights from table data for learning
        Queries rows and generates summaries
        """
        try:
            # Query rows
            rows = self.registry.query_rows(table_name, filters=filters, limit=100)
            
            insights = []
            
            for row in rows:
                row_dict = {
                    k: str(v) for k, v in row.__dict__.items()
                    if not k.startswith('_')
                }
                
                # Generate insight based on table type
                insight = await self._generate_insight(table_name, row_dict)
                if insight:
                    insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to extract insights: {e}")
            return []
    
    async def _generate_insight(self, table_name: str, row_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate an insight from a table row"""
        try:
            # Different insight generation based on table type
            if table_name == 'memory_documents':
                return {
                    'type': 'document_summary',
                    'title': row_data.get('title', 'Untitled'),
                    'topics': row_data.get('key_topics', []),
                    'trust': row_data.get('trust_score', 0.0),
                    'source': row_data.get('file_path')
                }
            
            elif table_name == 'memory_codebases':
                return {
                    'type': 'code_summary',
                    'repo': row_data.get('repo_name'),
                    'languages': row_data.get('languages', []),
                    'trust': row_data.get('trust_score', 0.0)
                }
            
            elif table_name == 'memory_datasets':
                return {
                    'type': 'data_summary',
                    'name': row_data.get('dataset_name'),
                    'rows': row_data.get('rows', 0),
                    'columns': row_data.get('columns', 0),
                    'trust': row_data.get('trust_score', 0.0)
                }
            
            elif table_name == 'memory_media':
                return {
                    'type': 'media_summary',
                    'file': row_data.get('file_path'),
                    'media_type': row_data.get('media_type'),
                    'topics': row_data.get('key_topics', [])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to generate insight: {e}")
            return None
    
    async def cross_domain_query(self, query_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute cross-domain queries across multiple tables
        Example: Find all documents + code + datasets related to "e-commerce"
        """
        try:
            results = {}
            
            # Query each table type
            if 'documents' in query_spec:
                results['documents'] = self.registry.query_rows(
                    'memory_documents',
                    filters=query_spec['documents'],
                    limit=50
                )
            
            if 'codebases' in query_spec:
                results['codebases'] = self.registry.query_rows(
                    'memory_codebases',
                    filters=query_spec['codebases'],
                    limit=50
                )
            
            if 'datasets' in query_spec:
                results['datasets'] = self.registry.query_rows(
                    'memory_datasets',
                    filters=query_spec['datasets'],
                    limit=50
                )
            
            if 'media' in query_spec:
                results['media'] = self.registry.query_rows(
                    'memory_media',
                    filters=query_spec['media'],
                    limit=50
                )
            
            # Convert to serializable format
            serialized = {}
            for table, rows in results.items():
                serialized[table] = [
                    {k: str(v) for k, v in row.__dict__.items() if not k.startswith('_')}
                    for row in rows
                ]
            
            return {
                'success': True,
                'results': serialized,
                'total_rows': sum(len(rows) for rows in results.values())
            }
            
        except Exception as e:
            logger.error(f"Cross-domain query failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def update_trust_scores(self, table_name: str):
        """
        Update trust scores for all rows in a table
        Integrates with clarity trust computation
        """
        try:
            rows = self.registry.query_rows(table_name, limit=10000)
            
            updated_count = 0
            
            for row in rows:
                # Compute new trust score
                new_score = await self._compute_trust_score(table_name, row)
                
                if new_score != row.trust_score:
                    # Update row
                    import uuid
                    self.registry.update_row(
                        table_name,
                        row.id if isinstance(row.id, uuid.UUID) else uuid.UUID(row.id),
                        {'trust_score': new_score}
                    )
                    updated_count += 1
            
            logger.info(f"✅ Updated {updated_count} trust scores in {table_name}")
            return updated_count
            
        except Exception as e:
            logger.error(f"Failed to update trust scores: {e}")
            return 0
    
    async def _compute_trust_score(self, table_name: str, row) -> float:
        """Compute trust score for a row"""
        # TODO: Integrate with clarity trust pipeline
        # For now, basic heuristics
        
        score = 0.5  # Base score
        
        # Has governance stamp?
        if hasattr(row, 'governance_stamp') and row.governance_stamp:
            score += 0.2
        
        # Has been synced?
        if hasattr(row, 'last_synced_at') and row.last_synced_at:
            score += 0.1
        
        # Has notes/annotations?
        if hasattr(row, 'notes') and row.notes:
            score += 0.1
        
        # Table-specific rules
        if table_name == 'memory_documents':
            if hasattr(row, 'token_count') and row.token_count > 1000:
                score += 0.1  # Substantial content
        
        return min(1.0, score)
    
    async def generate_learning_report(self) -> Dict[str, Any]:
        """Generate a report on learning status across all tables"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'tables': {},
                'summary': {}
            }
            
            for table_name in self.registry.list_tables():
                rows = self.registry.query_rows(table_name, limit=10000)
                
                # Compute stats
                total_rows = len(rows)
                synced_count = sum(1 for r in rows if hasattr(r, 'last_synced_at') and r.last_synced_at)
                avg_trust = sum(r.trust_score for r in rows if hasattr(r, 'trust_score')) / max(1, total_rows)
                
                report['tables'][table_name] = {
                    'total_rows': total_rows,
                    'synced_rows': synced_count,
                    'avg_trust_score': round(avg_trust, 3),
                    'sync_percentage': round(100 * synced_count / max(1, total_rows), 1)
                }
            
            # Summary
            report['summary'] = {
                'total_tables': len(report['tables']),
                'total_rows': sum(t['total_rows'] for t in report['tables'].values()),
                'overall_avg_trust': round(
                    sum(t['avg_trust_score'] * t['total_rows'] for t in report['tables'].values()) /
                    max(1, sum(t['total_rows'] for t in report['tables'].values())),
                    3
                )
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate learning report: {e}")
            return {'error': str(e)}


# Global instance
learning_bridge = MemoryTablesLearningBridge()
