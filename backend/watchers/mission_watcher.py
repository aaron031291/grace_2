"""
Mission Watcher - Auto-detect mission briefs in Learning Memory

Monitors storage/memory/learning/ for new mission briefs and automatically
triggers the mission orchestration pipeline.

Features:
- Watches for new .json files tagged with mission_brief
- Auto-detects mission intent from filenames/content
- Triggers mentor consultation and planning
- Publishes mission.detected events
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
import asyncio
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from backend.clarity import get_event_bus, Event
from backend.kernels.mission_orchestrator import get_mission_orchestrator


class MissionBriefHandler(FileSystemEventHandler):
    """Handler for mission brief file events"""
    
    def __init__(self, orchestrator_callback):
        self.orchestrator_callback = orchestrator_callback
        self.processed_files = set()
        
    def on_created(self, event):
        """Handle new file creation"""
        
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Check if it's a mission brief
        if self._is_mission_brief(file_path):
            # Avoid duplicate processing
            if str(file_path) not in self.processed_files:
                self.processed_files.add(str(file_path))
                # Trigger async processing
                asyncio.create_task(self.orchestrator_callback(file_path))
    
    def _is_mission_brief(self, file_path: Path) -> bool:
        """Check if file is a mission brief"""
        
        # Check filename
        if "brief" in file_path.name.lower() or "mission" in file_path.name.lower():
            return True
        
        # Check if in mission_briefs folder
        if "mission_briefs" in str(file_path):
            return True
        
        # Check JSON content for mission markers
        if file_path.suffix == '.json':
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    if "mission_id" in data or "objectives" in data:
                        return True
            except:
                pass
        
        return False


class MissionWatcher:
    """
    Watches Learning Memory for new mission briefs and auto-triggers orchestration
    """
    
    def __init__(self):
        self.event_bus = get_event_bus()
        self.orchestrator = get_mission_orchestrator()
        self.observer: Optional[Observer] = None
        self.watch_path = Path("storage/memory/learning")
        self.running = False
        
    async def start(self):
        """Start watching for mission briefs"""
        
        if self.running:
            return {"status": "already_running"}
        
        # Ensure watch directory exists
        self.watch_path.mkdir(parents=True, exist_ok=True)
        
        # Activate orchestrator
        await self.orchestrator.activate()
        
        # Create observer
        event_handler = MissionBriefHandler(self._process_mission_brief)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.watch_path), recursive=True)
        self.observer.start()
        
        self.running = True
        
        await self.event_bus.publish(Event(
            event_type="mission.watcher.started",
            source="mission_watcher",
            payload={"watch_path": str(self.watch_path)}
        ))
        
        return {
            "status": "started",
            "watch_path": str(self.watch_path),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def stop(self):
        """Stop watching"""
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        self.running = False
        
        await self.event_bus.publish(Event(
            event_type="mission.watcher.stopped",
            source="mission_watcher",
            payload={}
        ))
        
        return {"status": "stopped"}
    
    async def _process_mission_brief(self, file_path: Path):
        """Process detected mission brief"""
        
        try:
            # Load brief
            with open(file_path) as f:
                brief_data = json.load(f)
            
            mission_id = brief_data.get("mission_id") or file_path.stem
            brief_text = brief_data.get("objectives") or brief_data.get("description", "")
            constraints = brief_data.get("constraints", {})
            
            # Publish detection event
            await self.event_bus.publish(Event(
                event_type="mission.detected",
                source="mission_watcher",
                payload={
                    "mission_id": mission_id,
                    "file_path": str(file_path),
                    "auto_orchestration": True
                }
            ))
            
            # Check if auto-orchestration is enabled
            auto_orchestrate = brief_data.get("auto_orchestrate", True)
            
            if auto_orchestrate:
                # Trigger orchestration
                result = await self.orchestrator.execute_mission(
                    mission_id=mission_id,
                    brief=brief_text,
                    constraints=constraints,
                    auto_implement=brief_data.get("auto_implement", False)
                )
                
                # Publish completion
                await self.event_bus.publish(Event(
                    event_type="mission.auto_orchestrated",
                    source="mission_watcher",
                    payload={
                        "mission_id": mission_id,
                        "status": result["status"]
                    }
                ))
            
        except Exception as e:
            await self.event_bus.publish(Event(
                event_type="mission.watcher.error",
                source="mission_watcher",
                payload={
                    "file_path": str(file_path),
                    "error": str(e)
                }
            ))


# Global instance
_mission_watcher: Optional[MissionWatcher] = None


def get_mission_watcher() -> MissionWatcher:
    """Get global mission watcher instance"""
    global _mission_watcher
    if _mission_watcher is None:
        _mission_watcher = MissionWatcher()
    return _mission_watcher
