"""
Data Export and Backup System
Export all Grace's data, logs, and learning for backup or analysis
"""

import json
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import zipfile
import logging

from .models import async_session
from .healing_models import (
    HealingAttempt, AgenticSpineLog, MetaLoopLog,
    MLLearningLog, TriggerMeshLog, ShardLog, ParallelProcessLog, DataCubeEntry
)
from sqlalchemy import select

logger = logging.getLogger(__name__)


class DataExporter:
    """Export Grace's complete data for backup or analysis"""
    
    def __init__(self):
        self.export_dir = Path(__file__).parent.parent / "exports"
        self.export_dir.mkdir(exist_ok=True)
    
    async def export_all(self, format: str = "json") -> str:
        """
        Export all data from all tables
        
        Args:
            format: 'json' or 'csv'
        
        Returns:
            Path to export file
        """
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        export_name = f"grace_export_{timestamp}"
        export_path = self.export_dir / export_name
        export_path.mkdir(exist_ok=True)
        
        logger.info(f"[EXPORT] Starting full data export to {export_path}")
        
        # Export each table
        tables = [
            ('healing_attempts', HealingAttempt),
            ('agentic_spine_logs', AgenticSpineLog),
            ('meta_loop_logs', MetaLoopLog),
            ('ml_learning_logs', MLLearningLog),
            ('trigger_mesh_logs', TriggerMeshLog),
            ('shard_logs', ShardLog),
            ('parallel_process_logs', ParallelProcessLog),
            ('data_cube', DataCubeEntry)
        ]
        
        for table_name, model_class in tables:
            await self._export_table(table_name, model_class, export_path, format)
        
        # Create zip archive
        zip_path = self.export_dir / f"{export_name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in export_path.glob('*'):
                zipf.write(file, file.name)
        
        logger.info(f"[EXPORT] ✅ Export complete: {zip_path}")
        
        return str(zip_path)
    
    async def _export_table(
        self,
        table_name: str,
        model_class,
        export_path: Path,
        format: str
    ):
        """Export single table"""
        
        async with async_session() as session:
            result = await session.execute(select(model_class))
            entries = result.scalars().all()
            
            if format == 'json':
                # Export as JSON
                data = []
                for entry in entries:
                    entry_dict = {
                        column.name: getattr(entry, column.name)
                        for column in entry.__table__.columns
                    }
                    # Convert datetime to string
                    for key, value in entry_dict.items():
                        if isinstance(value, datetime):
                            entry_dict[key] = value.isoformat()
                    data.append(entry_dict)
                
                file_path = export_path / f"{table_name}.json"
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            
            elif format == 'csv':
                # Export as CSV
                if not entries:
                    return
                
                file_path = export_path / f"{table_name}.csv"
                
                columns = [col.name for col in entries[0].__table__.columns]
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=columns)
                    writer.writeheader()
                    
                    for entry in entries:
                        row = {col: getattr(entry, col) for col in columns}
                        # Convert datetime to string
                        for key, value in row.items():
                            if isinstance(value, datetime):
                                row[key] = value.isoformat()
                        writer.writerow(row)
            
            logger.debug(f"[EXPORT] Exported {len(entries)} entries from {table_name}")
    
    async def export_learning_only(self) -> str:
        """Export only ML/DL learning data"""
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_path = self.export_dir / f"learning_export_{timestamp}.json"
        
        async with async_session() as session:
            result = await session.execute(select(MLLearningLog))
            logs = result.scalars().all()
            
            data = []
            for log in logs:
                data.append({
                    'learning_id': log.learning_id,
                    'learning_type': log.learning_type,
                    'pattern_name': log.pattern_name,
                    'pattern_success_rate': log.pattern_success_rate,
                    'confidence': log.pattern_confidence,
                    'timestamp': log.timestamp.isoformat() if log.timestamp else None
                })
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        
        logger.info(f"[EXPORT] ✅ Exported {len(data)} learning entries")
        
        return str(file_path)
    
    async def backup_crypto_chains(self) -> str:
        """Backup all cryptographic chains for verification"""
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_path = self.export_dir / f"crypto_backup_{timestamp}.json"
        
        backup = {
            'timestamp': timestamp,
            'chains': {}
        }
        
        tables = [
            ('healing_attempts', HealingAttempt),
            ('agentic_spine_logs', AgenticSpineLog),
            ('meta_loop_logs', MetaLoopLog),
            ('ml_learning_logs', MLLearningLog)
        ]
        
        async with async_session() as session:
            for table_name, model_class in tables:
                result = await session.execute(select(model_class))
                entries = result.scalars().all()
                
                chain = []
                for entry in entries:
                    chain.append({
                        'id': entry.id,
                        'hash': entry.hash,
                        'previous_hash': entry.previous_hash,
                        'signature': entry.signature,
                        'timestamp': entry.created_at.isoformat() if hasattr(entry, 'created_at') and entry.created_at else None
                    })
                
                backup['chains'][table_name] = chain
        
        with open(file_path, 'w') as f:
            json.dump(backup, f, indent=2)
        
        logger.info(f"[EXPORT] ✅ Backed up crypto chains: {file_path}")
        
        return str(file_path)


# Global instance
data_exporter = DataExporter()
