"""
Presence System
Tracks who's viewing/editing what in real-time
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class PresenceSystem:
    """
    Manages user presence in the Memory Workspace.
    Tracks who is viewing/editing files, tables, and rows.
    """
    
    def __init__(self):
        # Active sessions: user_id -> session data
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # File viewers: file_path -> set of user_ids
        self.file_viewers: Dict[str, Set[str]] = defaultdict(set)
        
        # File editors: file_path -> user_id (exclusive lock)
        self.file_editors: Dict[str, str] = {}
        
        # Edit requests: file_path -> list of pending requests
        self.edit_requests: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Table viewers: table_name -> set of user_ids
        self.table_viewers: Dict[str, Set[str]] = defaultdict(set)
        
        # Row editors: (table_name, row_id) -> user_id
        self.row_editors: Dict[tuple, str] = {}
        
        # Heartbeat tracking
        self.last_heartbeat: Dict[str, datetime] = {}
        
        # Cleanup task
        self._cleanup_task = None
        self._running = False
    
    async def start(self):
        """Start presence monitoring"""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("👥 Presence system started")
    
    async def stop(self):
        """Stop presence monitoring"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
        logger.info("🛑 Presence system stopped")
    
    async def _cleanup_loop(self):
        """Clean up stale sessions"""
        while self._running:
            try:
                await self._cleanup_stale_sessions()
                await asyncio.sleep(30)  # Every 30 seconds
            except Exception as e:
                logger.error(f"Error in presence cleanup: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_stale_sessions(self):
        """Remove sessions with no heartbeat in 2 minutes"""
        cutoff = datetime.utcnow() - timedelta(minutes=2)
        stale_users = []
        
        for user_id, last_seen in self.last_heartbeat.items():
            if last_seen < cutoff:
                stale_users.append(user_id)
        
        for user_id in stale_users:
            await self.remove_user(user_id)
            logger.info(f"🧹 Removed stale session: {user_id}")
    
    async def join_session(
        self,
        user_id: str,
        user_name: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """User joins workspace session"""
        self.active_sessions[user_id] = {
            'user_id': user_id,
            'user_name': user_name,
            'metadata': metadata or {},
            'joined_at': datetime.utcnow().isoformat(),
            'current_view': None,
            'current_file': None,
            'current_table': None
        }
        
        self.last_heartbeat[user_id] = datetime.utcnow()
        
        logger.info(f"👤 {user_name} joined session")
        
        return {
            'success': True,
            'session': self.active_sessions[user_id],
            'active_users': len(self.active_sessions)
        }
    
    async def heartbeat(self, user_id: str) -> Dict[str, Any]:
        """Update user heartbeat"""
        self.last_heartbeat[user_id] = datetime.utcnow()
        
        return {
            'success': True,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def view_file(self, user_id: str, file_path: str):
        """User is viewing a file"""
        if user_id in self.active_sessions:
            self.active_sessions[user_id]['current_file'] = file_path
            self.active_sessions[user_id]['current_view'] = 'file'
        
        self.file_viewers[file_path].add(user_id)
        self.last_heartbeat[user_id] = datetime.utcnow()
    
    async def view_table(self, user_id: str, table_name: str):
        """User is viewing a table"""
        if user_id in self.active_sessions:
            self.active_sessions[user_id]['current_table'] = table_name
            self.active_sessions[user_id]['current_view'] = 'table'
        
        self.table_viewers[table_name].add(user_id)
        self.last_heartbeat[user_id] = datetime.utcnow()
    
    async def request_edit(
        self,
        user_id: str,
        user_name: str,
        file_path: str
    ) -> Dict[str, Any]:
        """Request edit permission for a file"""
        # Check if file is currently being edited
        if file_path in self.file_editors:
            current_editor = self.file_editors[file_path]
            
            if current_editor == user_id:
                return {
                    'success': True,
                    'granted': True,
                    'message': 'You already have edit permission'
                }
            
            # File is locked by someone else
            editor_session = self.active_sessions.get(current_editor, {})
            editor_name = editor_session.get('user_name', 'Unknown')
            
            # Add to pending requests
            request = {
                'user_id': user_id,
                'user_name': user_name,
                'requested_at': datetime.utcnow().isoformat()
            }
            self.edit_requests[file_path].append(request)
            
            return {
                'success': True,
                'granted': False,
                'locked_by': {
                    'user_id': current_editor,
                    'user_name': editor_name
                },
                'message': f'File is being edited by {editor_name}. Request sent.',
                'pending_position': len(self.edit_requests[file_path])
            }
        
        # Grant edit permission
        self.file_editors[file_path] = user_id
        
        return {
            'success': True,
            'granted': True,
            'message': 'Edit permission granted'
        }
    
    async def release_edit(self, user_id: str, file_path: str):
        """Release edit lock on a file"""
        if self.file_editors.get(file_path) == user_id:
            del self.file_editors[file_path]
            
            # Grant to next person in queue
            if file_path in self.edit_requests and self.edit_requests[file_path]:
                next_request = self.edit_requests[file_path].pop(0)
                next_user = next_request['user_id']
                self.file_editors[file_path] = next_user
                
                logger.info(f"🔓 Edit lock transferred: {file_path} → {next_request['user_name']}")
                
                return {
                    'success': True,
                    'transferred_to': next_request
                }
            
            logger.info(f"🔓 Edit lock released: {file_path}")
            return {'success': True}
        
        return {'success': False, 'error': 'You do not have edit lock'}
    
    async def request_edit_row(
        self,
        user_id: str,
        table_name: str,
        row_id: str
    ) -> Dict[str, Any]:
        """Request edit permission for a table row"""
        key = (table_name, row_id)
        
        if key in self.row_editors:
            current_editor = self.row_editors[key]
            
            if current_editor == user_id:
                return {'success': True, 'granted': True}
            
            return {
                'success': True,
                'granted': False,
                'locked_by': current_editor
            }
        
        self.row_editors[key] = user_id
        return {'success': True, 'granted': True}
    
    async def release_edit_row(
        self,
        user_id: str,
        table_name: str,
        row_id: str
    ):
        """Release edit lock on a row"""
        key = (table_name, row_id)
        
        if self.row_editors.get(key) == user_id:
            del self.row_editors[key]
            return {'success': True}
        
        return {'success': False}
    
    async def get_file_presence(self, file_path: str) -> Dict[str, Any]:
        """Get presence info for a file"""
        viewers = list(self.file_viewers.get(file_path, []))
        editor = self.file_editors.get(file_path)
        pending_requests = self.edit_requests.get(file_path, [])
        
        viewer_names = [
            self.active_sessions.get(uid, {}).get('user_name', uid)
            for uid in viewers
        ]
        
        editor_name = None
        if editor:
            editor_name = self.active_sessions.get(editor, {}).get('user_name', editor)
        
        return {
            'viewers': viewer_names,
            'viewer_count': len(viewers),
            'editor': editor_name,
            'is_locked': editor is not None,
            'pending_requests': len(pending_requests)
        }
    
    async def get_all_presence(self) -> Dict[str, Any]:
        """Get overall presence information"""
        active_users = []
        
        for user_id, session in self.active_sessions.items():
            active_users.append({
                'user_id': user_id,
                'user_name': session['user_name'],
                'current_view': session.get('current_view'),
                'current_file': session.get('current_file'),
                'current_table': session.get('current_table'),
                'last_seen': self.last_heartbeat.get(user_id, datetime.utcnow()).isoformat()
            })
        
        return {
            'active_users': active_users,
            'total_sessions': len(self.active_sessions),
            'files_being_viewed': len(self.file_viewers),
            'files_being_edited': len(self.file_editors),
            'rows_being_edited': len(self.row_editors)
        }
    
    async def remove_user(self, user_id: str):
        """Remove user from all presence tracking"""
        # Remove from active sessions
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
        
        # Remove from file viewers
        for viewers in self.file_viewers.values():
            viewers.discard(user_id)
        
        # Release file locks
        files_to_release = [
            path for path, editor in self.file_editors.items()
            if editor == user_id
        ]
        for file_path in files_to_release:
            await self.release_edit(user_id, file_path)
        
        # Release row locks
        rows_to_release = [
            key for key, editor in self.row_editors.items()
            if editor == user_id
        ]
        for key in rows_to_release:
            del self.row_editors[key]
        
        # Remove heartbeat
        if user_id in self.last_heartbeat:
            del self.last_heartbeat[user_id]


# Global instance
presence_system = PresenceSystem()
