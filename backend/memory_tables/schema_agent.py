#!/usr/bin/env python3
"""
LLM Schema Inference Agent
Analyzes file content and proposes appropriate database schemas
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SchemaInferenceAgent:
    """
    Uses LLM to infer database schemas from file analysis
    """
    
    def __init__(self, llm_client=None, registry=None):
        self.llm = llm_client
        self.registry = registry
    
    async def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a file and extract structural information
        Returns a summary suitable for schema inference
        """
        file_summary = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_size': file_path.stat().st_size if file_path.exists() else 0,
            'extension': file_path.suffix,
            'detected_type': None,
            'features': {},
            'sample_content': None
        }
        
        # Determine file type
        ext = file_path.suffix.lower()
        
        if ext in ['.pdf', '.txt', '.md', '.doc', '.docx']:
            file_summary['detected_type'] = 'document'
            file_summary['features'] = await self._analyze_document(file_path)
        
        elif ext in ['.py', '.js', '.ts', '.go', '.rs', '.java', '.cpp']:
            file_summary['detected_type'] = 'code'
            file_summary['features'] = await self._analyze_code(file_path)
        
        elif ext in ['.csv', '.json', '.parquet', '.xlsx']:
            file_summary['detected_type'] = 'dataset'
            file_summary['features'] = await self._analyze_dataset(file_path)
        
        elif ext in ['.mp3', '.wav', '.mp4', '.avi', '.jpg', '.png']:
            file_summary['detected_type'] = 'media'
            file_summary['features'] = await self._analyze_media(file_path)
        
        else:
            file_summary['detected_type'] = 'unknown'
        
        return file_summary
    
    async def _analyze_document(self, file_path: Path) -> Dict[str, Any]:
        """Extract features from a document"""
        features = {
            'has_title': False,
            'has_author': False,
            'estimated_pages': 0,
            'estimated_tokens': 0,
            'detected_sections': [],
            'language': 'en'
        }
        
        # TODO: Implement actual document analysis
        # For now, return basic info
        if file_path.suffix == '.txt' and file_path.exists():
            try:
                text = file_path.read_text(encoding='utf-8', errors='ignore')
                features['estimated_tokens'] = len(text.split())
                lines = text.split('\n')
                if lines:
                    features['has_title'] = bool(lines[0].strip())
            except Exception as e:
                logger.error(f"Error analyzing document: {e}")
        
        return features
    
    async def _analyze_code(self, file_path: Path) -> Dict[str, Any]:
        """Extract features from code"""
        features = {
            'language': file_path.suffix[1:],  # Remove the dot
            'has_imports': False,
            'has_classes': False,
            'has_functions': False,
            'entry_point': False,
            'dependencies': []
        }
        
        # Basic code analysis
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                features['has_imports'] = 'import ' in content
                features['has_classes'] = 'class ' in content
                features['has_functions'] = 'def ' in content or 'function ' in content
            except Exception as e:
                logger.error(f"Error analyzing code: {e}")
        
        return features
    
    async def _analyze_dataset(self, file_path: Path) -> Dict[str, Any]:
        """Extract features from a dataset"""
        features = {
            'format': file_path.suffix[1:],
            'has_headers': False,
            'estimated_rows': 0,
            'estimated_columns': 0,
            'column_names': [],
            'column_types': []
        }
        
        # Basic dataset analysis
        if file_path.suffix == '.csv' and file_path.exists():
            try:
                import csv
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    if rows:
                        features['has_headers'] = True
                        features['column_names'] = rows[0]
                        features['estimated_columns'] = len(rows[0])
                        features['estimated_rows'] = len(rows) - 1
            except Exception as e:
                logger.error(f"Error analyzing dataset: {e}")
        
        elif file_path.suffix == '.json' and file_path.exists():
            try:
                data = json.loads(file_path.read_text(encoding='utf-8'))
                if isinstance(data, list) and data:
                    features['estimated_rows'] = len(data)
                    if isinstance(data[0], dict):
                        features['column_names'] = list(data[0].keys())
                        features['estimated_columns'] = len(data[0])
            except Exception as e:
                logger.error(f"Error analyzing JSON dataset: {e}")
        
        return features
    
    async def _analyze_media(self, file_path: Path) -> Dict[str, Any]:
        """Extract features from media files"""
        features = {
            'media_type': None,
            'duration': 0,
            'has_audio': False,
            'has_video': False,
            'resolution': None
        }
        
        ext = file_path.suffix.lower()
        if ext in ['.mp3', '.wav']:
            features['media_type'] = 'audio'
            features['has_audio'] = True
        elif ext in ['.mp4', '.avi']:
            features['media_type'] = 'video'
            features['has_audio'] = True
            features['has_video'] = True
        elif ext in ['.jpg', '.png', '.gif']:
            features['media_type'] = 'image'
        
        return features
    
    async def propose_schema(self, file_summary: Dict[str, Any], existing_tables: List[str]) -> Dict[str, Any]:
        """
        Use LLM to propose a schema based on file analysis
        """
        detected_type = file_summary.get('detected_type')
        
        # Map to existing table if applicable
        type_to_table = {
            'document': 'memory_documents',
            'code': 'memory_codebases',
            'dataset': 'memory_datasets',
            'media': 'memory_media'
        }
        
        recommended_table = type_to_table.get(detected_type, 'memory_documents')
        
        # Check if table exists
        if recommended_table in existing_tables:
            return {
                'action': 'use_existing',
                'table_name': recommended_table,
                'confidence': 0.9,
                'reason': f"File type '{detected_type}' matches existing table"
            }
        
        # If LLM is available, get a more sophisticated proposal
        if self.llm:
            proposal = await self._llm_propose_schema(file_summary, existing_tables)
            return proposal
        
        # Fallback: suggest creating the standard table
        return {
            'action': 'create_new',
            'table_name': recommended_table,
            'confidence': 0.7,
            'reason': f"Standard table for {detected_type} files",
            'schema_file': f"{recommended_table}.yaml"
        }
    
    async def _llm_propose_schema(self, file_summary: Dict[str, Any], existing_tables: List[str]) -> Dict[str, Any]:
        """
        Use LLM to create a sophisticated schema proposal
        """
        prompt = f"""Analyze this file and propose the best database schema approach:

File Analysis:
{json.dumps(file_summary, indent=2)}

Existing Tables:
{', '.join(existing_tables)}

Provide a schema proposal with:
1. Whether to use an existing table or create new one
2. Recommended table name
3. Additional fields needed (if extending existing table)
4. Confidence score (0-1)
5. Reasoning

Respond in JSON format:
{{
    "action": "use_existing" or "create_new" or "extend_existing",
    "table_name": "...",
    "additional_fields": [...],
    "confidence": 0.0-1.0,
    "reason": "..."
}}
"""
        
        try:
            # TODO: Call actual LLM
            # For now, return default proposal
            response = {
                'action': 'use_existing',
                'table_name': 'memory_documents',
                'confidence': 0.8,
                'reason': 'Matches document pattern'
            }
            return response
        except Exception as e:
            logger.error(f"LLM schema proposal failed: {e}")
            return {
                'action': 'use_existing',
                'table_name': 'memory_documents',
                'confidence': 0.5,
                'reason': 'Fallback due to LLM error'
            }
    
    async def extract_row_data(self, file_path: Path, table_name: str) -> Dict[str, Any]:
        """
        Extract data to populate a table row
        """
        file_summary = await self.analyze_file(file_path)
        features = file_summary.get('features', {})
        
        # Base data common to all tables
        row_data = {
            'file_path': str(file_path),
            'trust_score': 0.0,
            'notes': f"Auto-imported on {datetime.now().isoformat()}"
        }
        
        # Table-specific data extraction
        if table_name == 'memory_documents':
            row_data.update({
                'title': file_path.stem.replace('_', ' ').title(),
                'authors': [],
                'source_type': 'custom',
                'summary': '',
                'key_topics': [],
                'token_count': features.get('estimated_tokens', 0),
                'risk_level': 'low'
            })
        
        elif table_name == 'memory_codebases':
            row_data.update({
                'repo_name': file_path.stem,
                'root_path': str(file_path.parent),
                'languages': [features.get('language', 'unknown')],
                'entry_points': [],
                'dependency_files': []
            })
        
        elif table_name == 'memory_datasets':
            row_data.update({
                'dataset_name': file_path.stem,
                'rows': features.get('estimated_rows', 0),
                'columns': features.get('estimated_columns', 0),
                'column_schema': [
                    {'name': col, 'type': 'unknown'}
                    for col in features.get('column_names', [])
                ],
                'risk_level': 'medium'
            })
        
        elif table_name == 'memory_media':
            row_data.update({
                'media_type': features.get('media_type', 'image'),
                'duration_seconds': features.get('duration', 0),
                'key_topics': [],
                'speakers': []
            })
        
        return row_data
