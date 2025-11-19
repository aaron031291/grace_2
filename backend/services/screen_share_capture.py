"""
Screen Share Capture Service with Learning Integration

Captures screen share frames, extracts content via vision pipeline,
and feeds into Grace's learning systems with governance controls.

Features:
- Frame capture and recording
- OCR text extraction
- Metadata extraction (window titles, app names)
- Speech-to-text for audio
- Learning mode (learn vs observe-only)
- Governance gating for sensitive content
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path
import logging
import uuid

logger = logging.getLogger(__name__)


class ScreenShareMode:
    """Screen share capture modes."""
    LEARN = "learn"  # Capture and ingest into learning systems
    OBSERVE = "observe_only"  # Capture but don't store
    CONSENT_REQUIRED = "consent_required"  # Require approval before storing


class ScreenShareCapture:
    """
    Screen share capture service with vision pipeline integration.
    
    Workflow:
    1. User starts screen share (with mode: learn | observe_only)
    2. Frames captured periodically (configurable fps)
    3. Vision pipeline processes frames:
       - OCR for text extraction
       - Object detection for metadata
       - Context extraction (app names, window titles)
    4. If mode = learn:
       - Check governance for sensitive content
       - Enqueue to learning pipeline
       - Store with provenance tracking
    5. Store context in world model
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.capture_interval = 5.0  # Capture frame every 5 seconds
        self.frame_storage_path = Path("storage/screen_captures")
        self.frame_storage_path.mkdir(parents=True, exist_ok=True)
    
    async def start_session(
        self,
        session_id: str,
        user_id: str,
        mode: str = ScreenShareMode.LEARN,
        quality: str = "medium",
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Start screen share capture session.
        
        Args:
            session_id: Unique session identifier
            user_id: User who initiated share
            mode: learn | observe_only | consent_required
            quality: low | medium | high
            metadata: Additional context
        
        Returns:
            Session info with capture settings
        """
        logger.info(f"[SCREEN-CAPTURE] Starting session {session_id} (mode: {mode})")
        
        session = {
            'session_id': session_id,
            'user_id': user_id,
            'mode': mode,
            'quality': quality,
            'status': 'active',
            'started_at': datetime.now(timezone.utc).isoformat(),
            'frames_captured': 0,
            'frames_learned': 0,
            'text_extracted': [],
            'metadata': metadata or {},
            'requires_governance': mode == ScreenShareMode.CONSENT_REQUIRED,
            'awaiting_approval': []
        }
        
        self.active_sessions[session_id] = session
        
        # Start capture loop
        asyncio.create_task(self._capture_loop(session_id))
        
        return {
            'session_id': session_id,
            'status': 'active',
            'mode': mode,
            'stream_url': f'/stream/{session_id}',
            'capture_settings': {
                'interval_seconds': self.capture_interval,
                'quality': quality,
                'learning_enabled': mode == ScreenShareMode.LEARN
            }
        }
    
    async def stop_session(self, session_id: str) -> Dict[str, Any]:
        """Stop screen share capture session."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session['status'] = 'stopped'
        session['stopped_at'] = datetime.now(timezone.utc).isoformat()
        
        logger.info(
            f"[SCREEN-CAPTURE] Session {session_id} stopped. "
            f"Captured: {session['frames_captured']}, Learned: {session['frames_learned']}"
        )
        
        # Archive session
        archived = self.active_sessions.pop(session_id)
        
        return {
            'session_id': session_id,
            'status': 'stopped',
            'frames_captured': archived['frames_captured'],
            'frames_learned': archived['frames_learned'],
            'duration_seconds': self._calculate_duration(archived)
        }
    
    async def _capture_loop(self, session_id: str):
        """Background loop to capture frames periodically."""
        while session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            if session['status'] != 'active':
                break
            
            try:
                # Capture frame (simulated - in production would use actual screen capture)
                frame_data = await self._capture_frame(session_id)
                
                if frame_data:
                    session['frames_captured'] += 1
                    
                    # Process through vision pipeline
                    await self._process_frame(session_id, frame_data)
            
            except Exception as e:
                logger.error(f"[SCREEN-CAPTURE] Frame capture failed: {e}")
            
            # Wait before next capture
            await asyncio.sleep(self.capture_interval)
    
    async def _capture_frame(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Capture a single frame from screen share.
        
        In production, this would:
        - Use Playwright/Selenium for browser capture
        - Use mss library for desktop capture
        - Use OpenCV for video processing
        
        For now, returns mock frame data.
        """
        # Mock frame data
        frame_id = f"{session_id}_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        return {
            'frame_id': frame_id,
            'session_id': session_id,
            'timestamp': timestamp,
            'format': 'image/png',
            'size': {'width': 1920, 'height': 1080},
            # In production: actual image data
            'data': f"<frame_data_{frame_id}>",
            'metadata': {
                'window_title': 'CRM Dashboard - Salesforce',
                'app_name': 'Google Chrome',
                'url': 'https://crm.example.com/dashboard'
            }
        }
    
    async def _process_frame(self, session_id: str, frame_data: Dict[str, Any]):
        """
        Process captured frame through vision pipeline.
        
        Steps:
        1. OCR text extraction
        2. Object detection / metadata extraction
        3. Governance check for sensitive content
        4. If approved, enqueue to learning pipeline
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        # Step 1: Extract text via OCR
        extracted_text = await self._ocr_extract(frame_data)
        
        # Step 2: Extract metadata
        metadata = await self._extract_metadata(frame_data)
        
        # Step 3: Check for sensitive content
        is_sensitive = await self._check_sensitive_content(extracted_text, metadata)
        
        # Step 4: Governance check
        if session['mode'] == ScreenShareMode.LEARN:
            if is_sensitive and session['requires_governance']:
                # Queue for approval
                approval_id = f"approval_{uuid.uuid4().hex[:8]}"
                session['awaiting_approval'].append({
                    'approval_id': approval_id,
                    'frame_id': frame_data['frame_id'],
                    'reason': 'Sensitive content detected',
                    'extracted_text': extracted_text[:200],
                    'timestamp': frame_data['timestamp']
                })
                
                logger.info(f"[SCREEN-CAPTURE] Frame {frame_data['frame_id']} queued for approval")
                
                # Send notification
                await self._send_approval_notification(session_id, approval_id, extracted_text)
            
            else:
                # Directly ingest
                await self._ingest_to_learning(session_id, frame_data, extracted_text, metadata)
                session['frames_learned'] += 1
        
        # Store extracted text in session history
        session['text_extracted'].append({
            'frame_id': frame_data['frame_id'],
            'timestamp': frame_data['timestamp'],
            'text': extracted_text[:500],  # Truncate
            'metadata': metadata
        })
    
    async def _ocr_extract(self, frame_data: Dict[str, Any]) -> str:
        """
        Extract text from frame using OCR.
        
        In production, would use:
        - Tesseract OCR
        - Google Cloud Vision API
        - Azure Computer Vision
        
        For now, returns mock extracted text.
        """
        # Mock OCR output based on metadata
        window_title = frame_data.get('metadata', {}).get('window_title', '')
        
        if 'CRM' in window_title or 'Dashboard' in window_title:
            return """
            Q4 Sales Pipeline - Active Deals
            
            Customer: Acme Corp
            Deal Value: $125,000
            Stage: Proposal Sent
            Close Date: Dec 15, 2025
            
            Customer: TechStart Inc
            Deal Value: $87,500
            Stage: Negotiation
            Close Date: Jan 10, 2026
            """
        
        elif 'Slides' in window_title or 'PowerPoint' in window_title:
            return """
            Product Roadmap Q1 2026
            
            Key Initiatives:
            - AI Integration Phase 2
            - Mobile App Redesign
            - Enterprise SSO
            
            Timeline: Jan - Mar 2026
            """
        
        else:
            return f"Screen content from {window_title or 'unknown app'}"
    
    async def _extract_metadata(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract contextual metadata from frame."""
        return {
            'source': 'screen_share',
            'window_title': frame_data.get('metadata', {}).get('window_title', ''),
            'app_name': frame_data.get('metadata', {}).get('app_name', ''),
            'url': frame_data.get('metadata', {}).get('url'),
            'timestamp': frame_data['timestamp'],
            'frame_id': frame_data['frame_id'],
            'resolution': frame_data.get('size', {})
        }
    
    async def _check_sensitive_content(self, text: str, metadata: Dict) -> bool:
        """
        Check if content contains sensitive information.
        
        Checks for:
        - PII (names, emails, phone numbers, SSN)
        - Financial data (credit cards, account numbers)
        - Credentials (passwords, API keys)
        - Proprietary information
        """
        sensitive_keywords = [
            'password', 'ssn', 'credit card', 'secret', 'confidential',
            'api_key', 'private key', 'token', 'salary', 'compensation'
        ]
        
        text_lower = text.lower()
        for keyword in sensitive_keywords:
            if keyword in text_lower:
                return True
        
        # Check URL for sensitive domains
        url = metadata.get('url', '').lower()
        if any(domain in url for domain in ['bank', 'payroll', 'hr', 'internal']):
            return True
        
        return False
    
    async def _ingest_to_learning(
        self,
        session_id: str,
        frame_data: Dict[str, Any],
        extracted_text: str,
        metadata: Dict[str, Any]
    ):
        """
        Ingest screen share content into learning pipeline.
        
        Same workflow as document upload:
        1. Chunk text
        2. Generate embeddings
        3. Store in RAG
        4. Update world model
        5. Log provenance
        """
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return
            
            # Build provenance
            source = f"ScreenShare: {metadata.get('window_title', 'Unknown')} @ {metadata['timestamp']}"
            
            # Step 1: Store in RAG
            try:
                from backend.services.rag_service import rag_service
                from backend.services.embedding_service import embedding_service
                
                await rag_service.initialize()
                await embedding_service.initialize()
                
                # Generate embedding
                embedding = await embedding_service.embed_text(
                    text=extracted_text,
                    source_type='screen_share'
                )
                
                # Store with metadata
                from backend.services.vector_store import vector_store
                await vector_store.initialize()
                
                await vector_store.store(
                    text=extracted_text,
                    embedding=embedding,
                    metadata={
                        'source': source,
                        'source_type': 'screen_share',
                        'session_id': session_id,
                        'user_id': session['user_id'],
                        'frame_id': frame_data['frame_id'],
                        'window_title': metadata.get('window_title'),
                        'app_name': metadata.get('app_name'),
                        'url': metadata.get('url'),
                        'timestamp': metadata['timestamp']
                    },
                    source_id=frame_data['frame_id']
                )
                
                logger.info(f"[SCREEN-CAPTURE] Frame {frame_data['frame_id']} ingested to RAG")
            
            except Exception as e:
                logger.error(f"[SCREEN-CAPTURE] RAG ingestion failed: {e}")
            
            # Step 2: Update world model
            try:
                from backend.world_model.grace_world_model import world_model
                await world_model.initialize()
                
                await world_model.add_knowledge(
                    content=f"Screen capture: {extracted_text[:200]}...",
                    source=source,
                    category="screen_share",
                    confidence=0.85,  # Medium confidence for screen content
                    metadata={
                        'session_id': session_id,
                        'user_id': session['user_id'],
                        'window_title': metadata.get('window_title'),
                        'captured_at': metadata['timestamp']
                    }
                )
                
                logger.info(f"[SCREEN-CAPTURE] Frame {frame_data['frame_id']} added to world model")
            
            except Exception as e:
                logger.error(f"[SCREEN-CAPTURE] World model update failed: {e}")
            
            # Step 3: Log to insights
            try:
                from backend.memory_tables.registry import table_registry
                
                if table_registry.has_table('memory_insights'):
                    table_registry.insert_row('memory_insights', {
                        'insight_type': 'screen_capture',
                        'source': source,
                        'content': f"Captured screen: {metadata.get('window_title', 'Unknown')}",
                        'metadata': {
                            'session_id': session_id,
                            'frame_id': frame_data['frame_id'],
                            'text_length': len(extracted_text),
                            'window_metadata': metadata
                        },
                        'created_at': datetime.utcnow().isoformat()
                    })
            
            except Exception as e:
                logger.error(f"[SCREEN-CAPTURE] Insight logging failed: {e}")
        
        except Exception as e:
            logger.error(f"[SCREEN-CAPTURE] Learning ingestion failed: {e}")
    
    async def _send_approval_notification(
        self,
        session_id: str,
        approval_id: str,
        content_preview: str
    ):
        """Send notification requesting approval for sensitive content."""
        try:
            from backend.routes.memory_events_api import memory_event_stream
            
            await memory_event_stream.publish('screen_share_approval_needed', {
                'session_id': session_id,
                'approval_id': approval_id,
                'message': f'Screen share captured sensitive content. Approval needed before learning.',
                'content_preview': content_preview[:100],
                'badge': '🔐',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        
        except Exception as e:
            logger.error(f"[SCREEN-CAPTURE] Notification failed: {e}")
    
    async def approve_frame(self, session_id: str, approval_id: str):
        """Approve a frame for learning after governance review."""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Find pending approval
        pending = next(
            (a for a in session['awaiting_approval'] if a['approval_id'] == approval_id),
            None
        )
        
        if not pending:
            raise ValueError(f"Approval {approval_id} not found")
        
        # Process the frame
        # (In production, would retrieve frame data from storage)
        frame_data = {
            'frame_id': pending['frame_id'],
            'timestamp': pending['timestamp']
        }
        
        extracted_text = pending['extracted_text']
        metadata = {'source': 'approved_screen_share'}
        
        await self._ingest_to_learning(session_id, frame_data, extracted_text, metadata)
        
        # Remove from pending
        session['awaiting_approval'] = [
            a for a in session['awaiting_approval']
            if a['approval_id'] != approval_id
        ]
        
        session['frames_learned'] += 1
        
        logger.info(f"[SCREEN-CAPTURE] Frame {pending['frame_id']} approved and learned")
        
        return {
            'success': True,
            'approval_id': approval_id,
            'frame_id': pending['frame_id']
        }
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a screen share session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return {'error': 'Session not found'}
        
        return {
            'session_id': session_id,
            'status': session['status'],
            'mode': session['mode'],
            'frames_captured': session['frames_captured'],
            'frames_learned': session['frames_learned'],
            'pending_approvals': len(session['awaiting_approval']),
            'text_extracted_count': len(session['text_extracted']),
            'duration_seconds': self._calculate_duration(session)
        }
    
    def _calculate_duration(self, session: Dict[str, Any]) -> float:
        """Calculate session duration in seconds."""
        started = datetime.fromisoformat(session['started_at'])
        
        if 'stopped_at' in session:
            stopped = datetime.fromisoformat(session['stopped_at'])
        else:
            stopped = datetime.now(timezone.utc)
        
        return (stopped - started).total_seconds()


# Singleton instance
screen_share_capture = ScreenShareCapture()
