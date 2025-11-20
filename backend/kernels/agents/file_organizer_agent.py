"""
File Organizer Agent - Intelligent file sorting and folder management
Analyzes content, determines domains, creates folders, and organizes files
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json
import shutil

from backend.clarity import BaseComponent, ComponentStatus, Event, TrustLevel, get_event_bus
from backend.database import get_db
from backend.core.unified_event_publisher import publish_event_obj


class FileOrganizerAgent(BaseComponent):
    """
    Intelligent file organization agent that:
    1. Analyzes file content to determine domain/topic
    2. Suggests or creates appropriate folder structure
    3. Moves files to relevant directories
    4. Learns from user corrections
    5. Provides undo/redo for all operations
    """
    
    def __init__(self):
        super().__init__()
        self.component_type = "file_organizer_agent"
        self.event_bus = get_event_bus()
        
        # Domain taxonomy (expandable)
        self.known_domains = {
            'business': ['startup', 'sales', 'marketing', 'strategy', 'business_intelligence'],
            'technical': ['code', 'documentation', 'api_discovery', 'codebases'],
            'finance': ['finance', 'crypto', 'compliance'],
            'research': ['research', 'datasets', 'insights'],
            'media': ['youtube', 'media', 'web_scraping', 'reddit'],
            'governance': ['governance', 'constitutional', 'safety'],
            'learning': ['learning', 'domain_knowledge', 'conversations']
        }
        
        # Operation history for undo
        self.operation_history: List[Dict[str, Any]] = []
        
    async def activate(self) -> bool:
        """Activate the file organizer agent"""
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        return True
    
    async def analyze_and_organize(self, file_path: Path, auto_move: bool = False) -> Dict[str, Any]:
        """
        Analyze file content and suggest/execute organization
        
        Args:
            file_path: Path to file to organize
            auto_move: If True, automatically move file. If False, just suggest.
            
        Returns:
            Organization result with suggestion and action taken
        """
        
        result = {
            'file_path': str(file_path),
            'status': 'analyzed',
            'suggestion': {},
            'action_taken': None,
            'confidence': 0.0,
            'reasoning': []
        }
        
        try:
            # Step 1: Determine domain based on content and filename
            domain_analysis = await self._analyze_domain(file_path)
            
            result['suggestion'] = {
                'domain': domain_analysis['domain'],
                'subdomain': domain_analysis['subdomain'],
                'target_folder': domain_analysis['target_folder'],
                'create_folder': domain_analysis.get('create_folder', False)
            }
            result['confidence'] = domain_analysis['confidence']
            result['reasoning'] = domain_analysis['reasoning']
            
            # Step 2: Check if target folder exists, create if needed
            target_path = Path(domain_analysis['target_folder'])
            
            if not target_path.exists() and domain_analysis.get('create_folder'):
                await self._create_folder(target_path, domain_analysis['domain'])
                result['reasoning'].append(f"Created new folder: {target_path}")
            
            # Step 3: Move file if auto_move or high confidence
            if auto_move or domain_analysis['confidence'] >= 0.85:
                move_result = await self._move_file(file_path, target_path)
                result['action_taken'] = 'moved'
                result['new_path'] = str(move_result['new_path'])
                result['operation_id'] = move_result['operation_id']
            else:
                result['action_taken'] = 'suggested'
                result['message'] = f"Suggested move to {target_path} (confidence: {domain_analysis['confidence']})"
            
            # Log to Librarian log
            await self._log_organization(result)
            
            # Publish event
            await publish_event_obj(
                event_type="file.organized" if result['action_taken'] == 'moved' else "file.organization_suggested",
                source=self.component_id,
                payload=result,
                trust_level=TrustLevel.HIGH if domain_analysis['confidence'] >= 0.85 else TrustLevel.MEDIUM
            )
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            
            await publish_event_obj(
                event_type="file.organization_failed",
                source=self.component_id,
                payload=result,
                trust_level=TrustLevel.LOW
            )
        
        return result
    
    async def _analyze_domain(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze file to determine appropriate domain/folder
        
        Uses:
        1. Filename analysis
        2. File extension
        3. Content analysis (first 1000 chars)
        4. Existing folder patterns
        """
        
        analysis = {
            'domain': 'uncategorized',
            'subdomain': None,
            'target_folder': None,
            'confidence': 0.0,
            'reasoning': []
        }
        
        filename = file_path.name.lower()
        extension = file_path.suffix.lower()
        
        # Rule 1: Filename keyword matching
        domain_keywords = {
            'business': ['business', 'startup', 'sales', 'marketing', 'pitch', 'revenue', 'customer'],
            'technical': ['code', 'api', 'tech', 'programming', 'software', 'debug', 'error'],
            'finance': ['finance', 'crypto', 'bitcoin', 'trading', 'investment', 'compliance'],
            'research': ['research', 'study', 'paper', 'analysis', 'dataset', 'insights'],
            'media': ['video', 'youtube', 'social', 'reddit', 'twitter', 'scrape'],
            'governance': ['governance', 'policy', 'constitution', 'safety', 'ethics'],
            'learning': ['learn', 'training', 'course', 'tutorial', 'lesson', 'knowledge'],
            'books': ['book', 'ebook', 'pdf', 'lean_startup', 'zero_to_one']
        }
        
        matched_domains = []
        for domain, keywords in domain_keywords.items():
            for keyword in keywords:
                if keyword in filename:
                    matched_domains.append(domain)
                    analysis['reasoning'].append(f"Filename contains '{keyword}' → {domain}")
                    break
        
        # Rule 2: File extension hints
        if extension == '.pdf' and 'book' in filename:
            matched_domains.append('books')
            analysis['reasoning'].append(f"PDF with 'book' in name → books")
        elif extension in ['.py', '.js', '.ts', '.java']:
            matched_domains.append('technical')
            analysis['reasoning'].append(f"Code file ({extension}) → technical")
        elif extension in ['.mp4', '.mp3', '.m4a']:
            matched_domains.append('media')
            analysis['reasoning'].append(f"Media file ({extension}) → media")
        elif extension in ['.csv', '.json', '.xlsx']:
            matched_domains.append('research')
            analysis['reasoning'].append(f"Data file ({extension}) → research")
        
        # Rule 3: Content analysis (if text file)
        if extension in ['.txt', '.md', '.rst']:
            content_hints = await self._analyze_content(file_path)
            if content_hints:
                matched_domains.extend(content_hints['domains'])
                analysis['reasoning'].extend(content_hints['reasoning'])
        
        # Determine final domain
        if matched_domains:
            # Most common match
            domain = max(set(matched_domains), key=matched_domains.count)
            analysis['domain'] = domain
            analysis['confidence'] = min(0.95, 0.6 + (matched_domains.count(domain) * 0.15))
        else:
            # No matches - use AI/LLM for deeper analysis (TODO)
            analysis['domain'] = 'uncategorized'
            analysis['confidence'] = 0.3
            analysis['reasoning'].append("No clear domain match, needs review")
        
        # Determine target folder
        base_path = Path('grace_training')
        
        if analysis['domain'] == 'books':
            analysis['target_folder'] = str(base_path / 'documents' / 'books')
        elif analysis['domain'] in self.known_domains:
            # Use existing structure
            category = None
            for cat, domains in self.known_domains.items():
                if analysis['domain'] in domains:
                    category = cat
                    break
            
            if category:
                analysis['target_folder'] = str(base_path / analysis['domain'])
            else:
                analysis['target_folder'] = str(base_path / analysis['domain'])
        else:
            # Create new domain folder
            analysis['target_folder'] = str(base_path / analysis['domain'])
            analysis['create_folder'] = True
            analysis['reasoning'].append(f"New domain detected, will create folder")
        
        return analysis
    
    async def _analyze_content(self, file_path: Path, max_chars: int = 1000) -> Optional[Dict]:
        """Analyze first N chars of file for domain hints"""
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_chars).lower()
            
            hints = {
                'domains': [],
                'reasoning': []
            }
            
            # Simple keyword density
            if content.count('startup') > 2 or content.count('business') > 3:
                hints['domains'].append('business')
                hints['reasoning'].append("Content mentions business/startup frequently")
            
            if content.count('code') > 2 or content.count('function') > 2:
                hints['domains'].append('technical')
                hints['reasoning'].append("Content discusses code/functions")
            
            if content.count('bitcoin') > 1 or content.count('crypto') > 1:
                hints['domains'].append('finance')
                hints['reasoning'].append("Content mentions cryptocurrency")
            
            return hints if hints['domains'] else None
            
        except Exception:
            return None
    
    async def _create_folder(self, folder_path: Path, domain: str) -> Dict[str, Any]:
        """Create new folder for a domain"""
        
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Create README
            readme_path = folder_path / 'README.md'
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"# {domain.replace('_', ' ').title()}\n\n")
                f.write(f"Auto-created by Grace Librarian on {datetime.utcnow().strftime('%Y-%m-%d')}\n\n")
                f.write(f"This folder contains files related to: **{domain}**\n")
            
            # Log creation
            await self._log_folder_creation(folder_path, domain)
            
            return {
                'status': 'created',
                'path': str(folder_path),
                'domain': domain
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _move_file(self, source: Path, target_folder: Path) -> Dict[str, Any]:
        """
        Move file to target folder with undo support
        
        Creates operation record for undo functionality
        """
        
        try:
            # Ensure target folder exists
            target_folder.mkdir(parents=True, exist_ok=True)
            
            # Generate target path
            target_path = target_folder / source.name
            
            # Handle name conflicts
            if target_path.exists():
                base = target_path.stem
                ext = target_path.suffix
                counter = 1
                while target_path.exists():
                    target_path = target_folder / f"{base}_{counter}{ext}"
                    counter += 1
            
            # Create backup for undo
            backup_path = await self._create_backup(source)
            
            # Move file
            shutil.move(str(source), str(target_path))
            
            # Record operation for undo
            operation = {
                'operation_id': f"move_{datetime.utcnow().timestamp()}",
                'type': 'move',
                'timestamp': datetime.utcnow().isoformat(),
                'source': str(source),
                'target': str(target_path),
                'backup_path': backup_path,
                'can_undo': True
            }
            
            self.operation_history.append(operation)
            await self._save_operation_to_db(operation)
            
            return {
                'status': 'success',
                'operation_id': operation['operation_id'],
                'new_path': str(target_path),
                'old_path': str(source)
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _create_backup(self, file_path: Path) -> str:
        """Create backup of file before moving (for undo)"""
        
        backup_dir = Path('.librarian_backups')
        backup_dir.mkdir(exist_ok=True)
        
        # Generate unique backup name
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        shutil.copy2(str(file_path), str(backup_path))
        
        return str(backup_path)
    
    async def undo_operation(self, operation_id: str) -> Dict[str, Any]:
        """
        Undo a file operation (move, delete, rename)
        
        Args:
            operation_id: ID of operation to undo
            
        Returns:
            Result of undo operation
        """
        
        # Find operation in history
        operation = None
        for op in self.operation_history:
            if op['operation_id'] == operation_id:
                operation = op
                break
        
        if not operation:
            return {
                'status': 'failed',
                'error': f"Operation {operation_id} not found in history"
            }
        
        if not operation.get('can_undo', False):
            return {
                'status': 'failed',
                'error': f"Operation {operation_id} cannot be undone"
            }
        
        try:
            if operation['type'] == 'move':
                # Restore from backup to original location
                source = Path(operation['source'])
                target = Path(operation['target'])
                backup = Path(operation['backup_path'])
                
                if target.exists():
                    # Move current file out of the way
                    shutil.move(str(target), str(target) + '.tmp')
                
                # Restore from backup
                shutil.copy2(str(backup), str(source))
                
                # Clean up
                if target.exists():
                    target.unlink()
                if (Path(str(target) + '.tmp')).exists():
                    Path(str(target) + '.tmp').unlink()
                
                operation['undone'] = True
                operation['undone_at'] = datetime.utcnow().isoformat()
                
                await self._save_operation_to_db(operation)
                
                await publish_event_obj(
                    event_type="file.operation_undone",
                    source=self.component_id,
                    payload={'operation_id': operation_id, 'type': 'move'},
                    trust_level=TrustLevel.HIGH
                )
                
                return {
                    'status': 'success',
                    'message': f"File restored to {source}",
                    'original_path': str(source)
                }
            
            elif operation['type'] == 'delete':
                # Restore from backup
                backup = Path(operation['backup_path'])
                target = Path(operation['target'])
                
                shutil.copy2(str(backup), str(target))
                
                operation['undone'] = True
                operation['undone_at'] = datetime.utcnow().isoformat()
                
                await self._save_operation_to_db(operation)
                
                return {
                    'status': 'success',
                    'message': f"File restored to {target}"
                }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def get_recent_operations(self, limit: int = 20) -> List[Dict]:
        """Get recent file operations for undo UI"""
        
        db = await get_db()
        
        operations = await db.fetch_all(
            """SELECT * FROM memory_file_operations
               ORDER BY timestamp DESC
               LIMIT ?""",
            (limit,)
        )
        
        return [dict(op) for op in operations]
    
    async def _log_organization(self, result: Dict[str, Any]):
        """Log organization action to Librarian log"""
        
        db = await get_db()
        
        await db.execute(
            """INSERT INTO memory_librarian_log
               (action_type, target_path, details, timestamp)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
            (
                'file_organization',
                result['file_path'],
                json.dumps(result)
            )
        )
        
        await db.commit()
    
    async def _log_folder_creation(self, folder_path: Path, domain: str):
        """Log folder creation"""
        
        db = await get_db()
        
        await db.execute(
            """INSERT INTO memory_librarian_log
               (action_type, target_path, details, timestamp)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
            (
                'folder_created',
                str(folder_path),
                json.dumps({'domain': domain, 'auto_created': True})
            )
        )
        
        await db.commit()
    
    async def _save_operation_to_db(self, operation: Dict[str, Any]):
        """Save operation to database for undo history"""
        
        db = await get_db()
        
        await db.execute(
            """INSERT OR REPLACE INTO memory_file_operations
               (operation_id, operation_type, source_path, target_path, 
                backup_path, can_undo, undone, timestamp, details)
               VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)""",
            (
                operation['operation_id'],
                operation['type'],
                operation.get('source'),
                operation.get('target'),
                operation.get('backup_path'),
                operation.get('can_undo', True),
                operation.get('undone', False),
                json.dumps(operation)
            )
        )
        
        await db.commit()
    
    async def learn_from_correction(self, file_path: str, user_chosen_folder: str):
        """
        Learn from user manually moving a file
        Updates domain rules for future classifications
        """
        
        # TODO: Implement machine learning from corrections
        # For now, log the correction
        
        db = await get_db()
        
        await db.execute(
            """INSERT INTO memory_file_organization_rules
               (file_pattern, target_folder, confidence, learned_from_user, created_at)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (
                Path(file_path).name,
                user_chosen_folder,
                0.7,
                True
            )
        )
        
        await db.commit()


# Singleton instance
_file_organizer = None

def get_file_organizer_agent() -> FileOrganizerAgent:
    global _file_organizer
    if _file_organizer is None:
        _file_organizer = FileOrganizerAgent()
    return _file_organizer
