"""
Log Service - Query and retrieve logs for inline display

Provides log access for chat responses, error surfacing, and debugging.
"""

import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path


class LogService:
    """
    Service for querying and retrieving logs
    
    Supports:
    - API error logs
    - Application logs
    - Execution logs
    - Self-healing logs
    - Audit logs
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
    
    async def get_recent_errors(
        self,
        count: int = 10,
        severity: str = "ERROR"
    ) -> List[Dict[str, Any]]:
        """
        Get recent error logs
        
        Args:
            count: Number of errors to return
            severity: Error severity (ERROR, WARNING, CRITICAL)
        
        Returns:
            List of error log entries
        """
        errors = []
        
        # Read error log file
        error_log = self.log_dir / "error.log"
        if error_log.exists():
            with open(error_log, 'r') as f:
                lines = f.readlines()
                
                # Parse error lines (assuming format: [timestamp] LEVEL message)
                for line in reversed(lines[-1000:]):  # Last 1000 lines
                    if severity in line:
                        match = re.match(r'\[(.*?)\]\s+(\w+)\s+(.*)', line.strip())
                        if match:
                            timestamp_str, level, message = match.groups()
                            errors.append({
                                "timestamp": timestamp_str,
                                "level": level,
                                "message": message,
                                "source": "error.log"
                            })
                            
                            if len(errors) >= count:
                                break
        
        return errors
    
    async def get_api_errors(
        self,
        endpoint: Optional[str] = None,
        count: int = 10,
        minutes_ago: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Get recent API errors
        
        Args:
            endpoint: Filter by specific endpoint (e.g., "/api/chat")
            count: Number of errors to return
            minutes_ago: Look back this many minutes
        
        Returns:
            List of API error entries
        """
        errors = []
        cutoff_time = datetime.now() - timedelta(minutes=minutes_ago)
        
        # Read access log for API errors (status >= 400)
        access_log = self.log_dir / "access.log"
        if access_log.exists():
            with open(access_log, 'r') as f:
                lines = f.readlines()
                
                for line in reversed(lines[-1000:]):
                    # Parse access log: timestamp endpoint status duration
                    match = re.search(r'\[(.*?)\].*?(\S+)\s+(\d{3})\s+(\d+)ms', line)
                    if match:
                        timestamp_str, path, status_code, duration = match.groups()
                        
                        # Filter by endpoint if specified
                        if endpoint and endpoint not in path:
                            continue
                        
                        # Only errors (status >= 400)
                        if int(status_code) >= 400:
                            errors.append({
                                "timestamp": timestamp_str,
                                "endpoint": path,
                                "status_code": int(status_code),
                                "duration_ms": int(duration),
                                "source": "access.log"
                            })
                            
                            if len(errors) >= count:
                                break
        
        return errors
    
    async def get_execution_logs(
        self,
        trace_id: Optional[str] = None,
        count: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get execution logs for action runs
        
        Args:
            trace_id: Filter by specific trace ID
            count: Number of log entries to return
        
        Returns:
            List of execution log entries
        """
        logs = []
        
        execution_log = self.log_dir / "execution.log"
        if execution_log.exists():
            with open(execution_log, 'r') as f:
                lines = f.readlines()
                
                for line in reversed(lines[-1000:]):
                    if trace_id and trace_id not in line:
                        continue
                    
                    # Parse execution log entry
                    match = re.match(r'\[(.*?)\].*?trace_id=(\S+)\s+(.*)', line.strip())
                    if match:
                        timestamp_str, tid, message = match.groups()
                        logs.append({
                            "timestamp": timestamp_str,
                            "trace_id": tid,
                            "message": message,
                            "source": "execution.log"
                        })
                        
                        if len(logs) >= count:
                            break
        
        return logs
    
    async def get_healing_logs(
        self,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get self-healing attempt logs
        
        Args:
            count: Number of healing logs to return
        
        Returns:
            List of healing log entries
        """
        logs = []
        
        healing_log = self.log_dir / "healing.log"
        if healing_log.exists():
            with open(healing_log, 'r') as f:
                lines = f.readlines()
                
                for line in reversed(lines[-1000:]):
                    match = re.match(r'\[(.*?)\]\s+(.*)', line.strip())
                    if match:
                        timestamp_str, message = match.groups()
                        logs.append({
                            "timestamp": timestamp_str,
                            "message": message,
                            "source": "healing.log"
                        })
                        
                        if len(logs) >= count:
                            break
        
        return logs
    
    async def search_logs(
        self,
        query: str,
        count: int = 20,
        log_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search logs for specific text
        
        Args:
            query: Search query
            count: Number of results to return
            log_type: Filter by log type (error, access, execution, healing)
        
        Returns:
            List of matching log entries
        """
        results = []
        
        # Determine which logs to search
        log_files = {
            "error": "error.log",
            "access": "access.log",
            "execution": "execution.log",
            "healing": "healing.log",
            "application": "grace.log"
        }
        
        if log_type:
            files_to_search = {log_type: log_files.get(log_type, "grace.log")}
        else:
            files_to_search = log_files
        
        # Search each log file
        for log_name, log_file in files_to_search.items():
            log_path = self.log_dir / log_file
            if log_path.exists():
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                    
                    for line in reversed(lines[-1000:]):
                        if query.lower() in line.lower():
                            results.append({
                                "log_type": log_name,
                                "content": line.strip(),
                                "source": log_file
                            })
                            
                            if len(results) >= count:
                                return results
        
        return results
    
    async def get_logs_by_intent(
        self,
        intent: str,
        count: int = 10
    ) -> Dict[str, Any]:
        """
        Get logs based on user intent (natural language)
        
        Args:
            intent: User's request (e.g., "show API errors", "latest logs", "deployment issues")
            count: Number of log entries to return
        
        Returns:
            Categorized log results
        """
        intent_lower = intent.lower()
        
        # Detect intent and route to appropriate method
        if "api" in intent_lower and ("error" in intent_lower or "fail" in intent_lower):
            return {
                "type": "api_errors",
                "logs": await self.get_api_errors(count=count),
                "summary": f"Recent API errors (last {count})"
            }
        
        elif "healing" in intent_lower or "self-heal" in intent_lower:
            return {
                "type": "healing",
                "logs": await self.get_healing_logs(count=count),
                "summary": f"Recent self-healing attempts (last {count})"
            }
        
        elif "execution" in intent_lower or "action" in intent_lower:
            return {
                "type": "execution",
                "logs": await self.get_execution_logs(count=count),
                "summary": f"Recent action executions (last {count})"
            }
        
        elif "error" in intent_lower or "fail" in intent_lower:
            return {
                "type": "errors",
                "logs": await self.get_recent_errors(count=count),
                "summary": f"Recent errors (last {count})"
            }
        
        else:
            # General search
            return {
                "type": "search",
                "logs": await self.search_logs(query=intent, count=count),
                "summary": f"Log search results for: {intent}"
            }


# Singleton instance
log_service = LogService()
