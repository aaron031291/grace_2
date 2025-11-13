"""
Session Recorder
Records all remote access sessions for audit and SIEM forwarding
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import logging

from ..unified_logger import unified_logger

logger = logging.getLogger(__name__)


class SessionRecorder:
    """
    Records everything Grace does during remote sessions
    - Terminal commands
    - File access
    - API calls
    - Code modifications
    - Forward to SIEM
    """
    
    def __init__(self):
        self.recordings_dir = Path('logs/remote_sessions')
        self.active_recordings = {}
        self.siem_enabled = False
    
    async def start(self):
        """Initialize session recorder"""
        
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("[SESSION-RECORDER] Started")
    
    async def start_recording(
        self,
        session_id: str,
        device_id: str,
        device_name: str
    ) -> str:
        """
        Start recording a session
        
        Returns:
            Recording ID
        """
        
        recording_id = f"rec_{session_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        recording = {
            'recording_id': recording_id,
            'session_id': session_id,
            'device_id': device_id,
            'device_name': device_name,
            'started_at': datetime.utcnow().isoformat(),
            'events': [],
            'commands': [],
            'file_access': [],
            'api_calls': [],
            'suspicious_activity': []
        }
        
        self.active_recordings[recording_id] = recording
        
        logger.info(f"[SESSION-RECORDER] Started recording: {recording_id} for {device_name}")
        
        return recording_id
    
    async def record_command(
        self,
        recording_id: str,
        command: str,
        output: str,
        exit_code: int,
        execution_time_ms: float
    ):
        """Record a command execution"""
        
        recording = self.active_recordings.get(recording_id)
        
        if not recording:
            logger.warning(f"[SESSION-RECORDER] Unknown recording: {recording_id}")
            return
        
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'command',
            'command': command,
            'output_length': len(output),
            'output_preview': output[:200] if len(output) > 200 else output,
            'exit_code': exit_code,
            'execution_time_ms': execution_time_ms,
            'suspicious': self._is_suspicious_command(command)
        }
        
        recording['events'].append(event)
        recording['commands'].append(command)
        
        # Check for suspicious activity
        if event['suspicious']:
            recording['suspicious_activity'].append(event)
            logger.warning(f"[SESSION-RECORDER] Suspicious command: {command}")
            
            # Alert immediately
            await self._alert_suspicious_activity(recording_id, event)
        
        # Forward to SIEM
        if self.siem_enabled:
            await self._forward_to_siem(recording_id, event)
    
    async def record_file_access(
        self,
        recording_id: str,
        file_path: str,
        access_type: str,  # read, write, delete, execute
        success: bool
    ):
        """Record file access"""
        
        recording = self.active_recordings.get(recording_id)
        
        if not recording:
            return
        
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'file_access',
            'file_path': file_path,
            'access_type': access_type,
            'success': success,
            'suspicious': self._is_suspicious_file_access(file_path, access_type)
        }
        
        recording['events'].append(event)
        recording['file_access'].append(event)
        
        if event['suspicious']:
            recording['suspicious_activity'].append(event)
            await self._alert_suspicious_activity(recording_id, event)
    
    async def record_api_call(
        self,
        recording_id: str,
        api_endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float
    ):
        """Record API call"""
        
        recording = self.active_recordings.get(recording_id)
        
        if not recording:
            return
        
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'api_call',
            'endpoint': api_endpoint,
            'method': method,
            'status_code': status_code,
            'response_time_ms': response_time_ms
        }
        
        recording['events'].append(event)
        recording['api_calls'].append(event)
    
    async def stop_recording(self, recording_id: str) -> Optional[str]:
        """
        Stop recording and save to file
        
        Returns:
            Path to recording file
        """
        
        recording = self.active_recordings.get(recording_id)
        
        if not recording:
            return None
        
        recording['finished_at'] = datetime.utcnow().isoformat()
        recording['total_events'] = len(recording['events'])
        recording['total_commands'] = len(recording['commands'])
        recording['total_suspicious'] = len(recording['suspicious_activity'])
        
        # Save to file
        recording_file = self.recordings_dir / f"{recording_id}.json"
        
        with open(recording_file, 'w', encoding='utf-8') as f:
            json.dump(recording, f, indent=2)
        
        # Log to unified logger
        await unified_logger.log_agentic_spine_decision(
            decision_type='session_recording',
            decision_context={
                'recording_id': recording_id,
                'total_events': recording['total_events'],
                'suspicious_count': recording['total_suspicious']
            },
            chosen_action='save_recording',
            rationale=f'Session recording completed',
            actor='session_recorder',
            confidence=1.0,
            risk_score=0.05,
            status='completed',
            resource=recording_id
        )
        
        # Remove from active
        del self.active_recordings[recording_id]
        
        logger.info(f"[SESSION-RECORDER] Recording saved: {recording_file}")
        
        return str(recording_file)
    
    def _is_suspicious_command(self, command: str) -> bool:
        """Check if command is suspicious"""
        
        suspicious_patterns = [
            'rm -rf /',
            'dd if=',
            'mkfs',
            'fdisk',
            'wget http://',  # Only HTTPS allowed
            'curl http://',
            'nc -l',  # Netcat listener
            'chmod 777',
            'sudo su',
            'passwd',
            '/etc/shadow',
            '/etc/passwd',
            'base64 -d',  # Encoded payloads
            'eval(',
            'exec(',
        ]
        
        cmd_lower = command.lower()
        
        return any(pattern in cmd_lower for pattern in suspicious_patterns)
    
    def _is_suspicious_file_access(self, file_path: str, access_type: str) -> bool:
        """Check if file access is suspicious"""
        
        suspicious_paths = [
            '/etc/shadow',
            '/etc/passwd',
            '.ssh/id_rsa',
            '.aws/credentials',
            'vault_key',
            'api_key',
            'secret',
            'password'
        ]
        
        path_lower = file_path.lower()
        
        # Write access to sensitive files
        if access_type in ['write', 'delete']:
            return any(pattern in path_lower for pattern in suspicious_paths)
        
        return False
    
    async def _alert_suspicious_activity(self, recording_id: str, event: Dict[str, Any]):
        """Alert on suspicious activity"""
        
        recording = self.active_recordings.get(recording_id)
        
        if not recording:
            return
        
        alert = {
            'alert_type': 'suspicious_remote_activity',
            'severity': 'high',
            'recording_id': recording_id,
            'device_id': recording['device_id'],
            'device_name': recording['device_name'],
            'event': event,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log alert
        await unified_logger.log_agentic_spine_decision(
            decision_type='security_alert',
            decision_context=alert,
            chosen_action='alert_admin',
            rationale=f'Suspicious activity detected in remote session',
            actor='session_recorder',
            confidence=0.9,
            risk_score=0.85,
            status='alerted',
            resource=recording_id
        )
        
        logger.warning(f"[SESSION-RECORDER] 🚨 ALERT: Suspicious activity in {recording_id}")
    
    async def _forward_to_siem(self, recording_id: str, event: Dict[str, Any]):
        """Forward event to SIEM system"""
        
        # In production, would forward to Splunk, ELK, etc.
        # For now, just log
        
        logger.info(f"[SESSION-RECORDER] SIEM: {event['type']} event")
    
    def get_recordings(self, device_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all recordings"""
        
        recordings = []
        
        for recording_file in self.recordings_dir.glob('*.json'):
            try:
                with open(recording_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if device_id and data.get('device_id') != device_id:
                    continue
                
                recordings.append({
                    'recording_id': data['recording_id'],
                    'device_name': data['device_name'],
                    'started_at': data['started_at'],
                    'finished_at': data.get('finished_at'),
                    'total_events': data.get('total_events', 0),
                    'suspicious_count': data.get('total_suspicious', 0),
                    'file_path': str(recording_file)
                })
            
            except:
                pass
        
        return sorted(recordings, key=lambda x: x['started_at'], reverse=True)


# Global instance
session_recorder = SessionRecorder()
