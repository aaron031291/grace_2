#!/usr/bin/env python3
"""
Content Analysis Pipeline
Extracts features from files for schema inference and table population
"""

import logging
from pathlib import Path
from typing import Dict, Any
import mimetypes

logger = logging.getLogger(__name__)


class ContentAnalysisPipeline:
    """
    Multi-stage pipeline for analyzing file content
    Feeds into schema inference and table population
    """
    
    def __init__(self):
        self.extractors = {
            'document': DocumentExtractor(),
            'code': CodeExtractor(),
            'dataset': DatasetExtractor(),
            'media': MediaExtractor()
        }
    
    async def analyze(self, file_path: Path) -> Dict[str, Any]:
        """
        Run full analysis pipeline on a file
        Returns comprehensive feature summary
        """
        result = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_size': file_path.stat().st_size if file_path.exists() else 0,
            'mime_type': mimetypes.guess_type(str(file_path))[0],
            'category': None,
            'features': {},
            'metadata': {},
            'errors': []
        }
        
        # Determine category
        category = self._categorize_file(file_path)
        result['category'] = category
        
        # Run appropriate extractor
        if category in self.extractors:
            try:
                extractor = self.extractors[category]
                features = await extractor.extract(file_path)
                result['features'] = features
            except Exception as e:
                logger.error(f"Extraction failed for {file_path}: {e}")
                result['errors'].append(str(e))
        
        return result
    
    def _categorize_file(self, file_path: Path) -> str:
        """Determine file category based on extension and mime type"""
        ext = file_path.suffix.lower()
        
        # Document extensions
        if ext in ['.pdf', '.txt', '.md', '.doc', '.docx', '.rtf', '.odt']:
            return 'document'
        
        # Code extensions
        if ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java', 
                   '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.swift', '.kt']:
            return 'code'
        
        # Dataset extensions
        if ext in ['.csv', '.json', '.jsonl', '.parquet', '.xlsx', '.xls', '.tsv']:
            return 'dataset'
        
        # Media extensions
        if ext in ['.mp3', '.wav', '.mp4', '.avi', '.mov', '.jpg', '.jpeg', 
                   '.png', '.gif', '.svg', '.webp']:
            return 'media'
        
        return 'unknown'


class DocumentExtractor:
    """Extract features from text documents"""
    
    async def extract(self, file_path: Path) -> Dict[str, Any]:
        features = {
            'title': None,
            'authors': [],
            'sections': [],
            'token_count': 0,
            'language': 'en',
            'has_toc': False,
            'page_count': 0
        }
        
        if not file_path.exists():
            return features
        
        ext = file_path.suffix.lower()
        
        if ext == '.txt' or ext == '.md':
            features.update(await self._extract_text(file_path))
        elif ext == '.pdf':
            features.update(await self._extract_pdf(file_path))
        
        return features
    
    async def _extract_text(self, file_path: Path) -> Dict[str, Any]:
        """Extract from plain text files"""
        try:
            text = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = text.split('\n')
            
            # Heuristics for title
            title = None
            if lines:
                first_line = lines[0].strip()
                if len(first_line) < 100 and first_line:
                    title = first_line
            
            # Token count (rough estimate)
            token_count = len(text.split())
            
            # Look for markdown sections
            sections = [line.strip('# ') for line in lines if line.startswith('#')]
            
            return {
                'title': title,
                'token_count': token_count,
                'sections': sections[:10],  # First 10 sections
                'page_count': max(1, token_count // 300)  # Rough page estimate
            }
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return {}
    
    async def _extract_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract from PDF files"""
        # TODO: Implement PDF extraction with pypdf or similar
        return {
            'title': file_path.stem,
            'format': 'pdf'
        }


class CodeExtractor:
    """Extract features from code files"""
    
    async def extract(self, file_path: Path) -> Dict[str, Any]:
        features = {
            'language': file_path.suffix[1:] if file_path.suffix else 'unknown',
            'imports': [],
            'classes': [],
            'functions': [],
            'lines_of_code': 0,
            'has_tests': False,
            'has_main': False
        }
        
        if not file_path.exists():
            return features
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            features['lines_of_code'] = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            
            # Language-specific parsing
            if file_path.suffix == '.py':
                features.update(self._parse_python(content))
            elif file_path.suffix in ['.js', '.ts']:
                features.update(self._parse_javascript(content))
            
            return features
        except Exception as e:
            logger.error(f"Code extraction failed: {e}")
            return features
    
    def _parse_python(self, content: str) -> Dict[str, Any]:
        """Basic Python parsing"""
        import re
        
        imports = re.findall(r'^(?:from|import)\s+(\S+)', content, re.MULTILINE)
        classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
        functions = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)
        
        return {
            'imports': imports[:20],
            'classes': classes[:20],
            'functions': functions[:20],
            'has_tests': 'test' in content.lower(),
            'has_main': '__main__' in content
        }
    
    def _parse_javascript(self, content: str) -> Dict[str, Any]:
        """Basic JavaScript/TypeScript parsing"""
        import re
        
        imports = re.findall(r'import\s+.*?from\s+[\'"](\S+)[\'"]', content)
        classes = re.findall(r'class\s+(\w+)', content)
        functions = re.findall(r'function\s+(\w+)|const\s+(\w+)\s*=.*?=>', content)
        
        return {
            'imports': imports[:20],
            'classes': classes[:20],
            'functions': [f[0] or f[1] for f in functions[:20]],
            'has_tests': 'test' in content.lower() or 'describe' in content
        }


class DatasetExtractor:
    """Extract features from datasets"""
    
    async def extract(self, file_path: Path) -> Dict[str, Any]:
        features = {
            'format': file_path.suffix[1:],
            'rows': 0,
            'columns': 0,
            'column_names': [],
            'column_types': {},
            'has_headers': False,
            'sample_data': []
        }
        
        if not file_path.exists():
            return features
        
        ext = file_path.suffix.lower()
        
        if ext == '.csv':
            features.update(await self._extract_csv(file_path))
        elif ext == '.json':
            features.update(await self._extract_json(file_path))
        
        return features
    
    async def _extract_csv(self, file_path: Path) -> Dict[str, Any]:
        """Extract from CSV files"""
        try:
            import csv
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if not rows:
                    return {}
                
                # Assume first row is headers
                headers = rows[0]
                data_rows = rows[1:]
                
                return {
                    'rows': len(data_rows),
                    'columns': len(headers),
                    'column_names': headers,
                    'has_headers': True,
                    'sample_data': data_rows[:5]
                }
        except Exception as e:
            logger.error(f"CSV extraction failed: {e}")
            return {}
    
    async def _extract_json(self, file_path: Path) -> Dict[str, Any]:
        """Extract from JSON files"""
        try:
            import json
            
            data = json.loads(file_path.read_text(encoding='utf-8'))
            
            if isinstance(data, list):
                rows = len(data)
                if data and isinstance(data[0], dict):
                    columns = list(data[0].keys())
                    return {
                        'rows': rows,
                        'columns': len(columns),
                        'column_names': columns,
                        'sample_data': data[:5]
                    }
            
            return {'format': 'json', 'rows': 1}
        except Exception as e:
            logger.error(f"JSON extraction failed: {e}")
            return {}


class MediaExtractor:
    """Extract features from media files"""
    
    async def extract(self, file_path: Path) -> Dict[str, Any]:
        ext = file_path.suffix.lower()
        
        features = {
            'format': ext[1:],
            'media_type': None,
            'duration': 0,
            'has_audio': False,
            'has_video': False,
            'width': 0,
            'height': 0
        }
        
        # Categorize media type
        if ext in ['.mp3', '.wav', '.ogg', '.flac']:
            features['media_type'] = 'audio'
            features['has_audio'] = True
        elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
            features['media_type'] = 'video'
            features['has_audio'] = True
            features['has_video'] = True
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
            features['media_type'] = 'image'
        
        # TODO: Extract actual metadata using ffmpeg/pillow
        
        return features


# Global pipeline instance
content_pipeline = ContentAnalysisPipeline()
