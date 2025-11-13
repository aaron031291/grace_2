"""
Librarian Kernel
Orchestrates memory workspace, schema management, ingestion, and trust curation
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .base_kernel import BaseDomainKernel
from backend.memory_tables.trusted_sources_integration import TrustedSourcesValidator

logger = logging.getLogger(__name__)


class FileSystemWatcher(FileSystemEventHandler):
    """Watches filesystem for changes"""
    
    def __init__(self, kernel):
        self.kernel = kernel
        self.queue = asyncio.Queue()
        self.loop = None  # Will be set when kernel starts
    
    def on_created(self, event: FileSystemEvent):
        if not event.is_directory and self.loop:
            # Check if it's a book file
            file_path = Path(event.src_path)
            is_book = 'books' in str(file_path) and file_path.suffix.lower() in ['.pdf', '.epub']
            
            # Schedule coroutine on the main event loop (thread-safe)
            asyncio.run_coroutine_threadsafe(
                self.queue.put({
                    'type': 'file_created',
                    'path': event.src_path,
                    'timestamp': datetime.utcnow().isoformat(),
                    'is_book': is_book,
                    'file_type': file_path.suffix.lower()
                }),
                self.loop
            )
    
    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory and self.loop:
            # Schedule coroutine on the main event loop (thread-safe)
            asyncio.run_coroutine_threadsafe(
                self.queue.put({
                    'type': 'file_modified',
                    'path': event.src_path,
                    'timestamp': datetime.utcnow().isoformat()
                }),
                self.loop
            )
    
    def on_deleted(self, event: FileSystemEvent):
        if self.loop:
            # Schedule coroutine on the main event loop (thread-safe)
            asyncio.run_coroutine_threadsafe(
                self.queue.put({
                    'type': 'file_deleted',
                    'path': event.src_path,
                    'timestamp': datetime.utcnow().isoformat()
                }),
                self.loop
            )


class LibrarianKernel(BaseDomainKernel):
    """
    Librarian Domain Kernel
    
    Responsibilities:
    - Monitor memory workspace (grace_training/, storage/uploads)
    - Route schema proposals through Unified Logic
    - Schedule ingestion/self-healing/verification jobs
    - Maintain trust dashboards
    - Spawn/terminate specialist sub-agents
    """
    
    def __init__(self, registry=None, event_bus=None):
        super().__init__(
            kernel_id='librarian_kernel',
            domain='memory_workspace',
            registry=registry,
            event_bus=event_bus
        )
        
        # Watch directories
        self.watch_paths = [
            Path('grace_training'),
            Path('storage/uploads'),
            Path('docs')
        ]
        
        # File system observer
        self.fs_observer: Optional[Observer] = None
        self.fs_handler: Optional[FileSystemWatcher] = None
        
        # Work queues
        self.schema_queue = asyncio.Queue()
        self.ingestion_queue = asyncio.Queue()
        self.trust_audit_queue = asyncio.Queue()
        
        # Trust validator
        self.trust_validator = TrustedSourcesValidator(registry) if registry else None
        
        # Agent capabilities
        self.agent_types = {
            'schema_scout': 'backend.kernels.agents.schema_scout.SchemaScout',
            'ingestion_runner': 'backend.kernels.agents.ingestion_runner.IngestionRunner',
            'flashcard_maker': 'backend.kernels.agents.flashcard_maker.FlashcardMaker',
            'trust_auditor': 'backend.kernels.agents.trust_auditor.TrustAuditor'
        }
        
        # Kernel config
        self.config = {
            'max_concurrent_agents': 5,
            'schema_auto_approve_threshold': 0.8,
            'trust_audit_interval': 3600,  # 1 hour
            'heartbeat_interval': 30  # 30 seconds
        }
    
    async def _initialize_watchers(self):
        """Set up filesystem watchers and event listeners"""
        logger.info("Initializing Librarian watchers...")
        
        # Capture the running event loop for thread-safe event dispatch
        loop = asyncio.get_running_loop()
        
        # Create watch directories if they don't exist
        for path in self.watch_paths:
            path.mkdir(parents=True, exist_ok=True)
        
        # Setup filesystem watcher
        self.fs_handler = FileSystemWatcher(self)
        self.fs_handler.loop = loop  # Set the event loop for thread-safe operations
        self.fs_observer = Observer()
        
        for path in self.watch_paths:
            if path.exists():
                self.fs_observer.schedule(
                    self.fs_handler,
                    str(path),
                    recursive=True
                )
                logger.info(f"Watching: {path}")
        
        self.fs_observer.start()
        
        # Start filesystem event processor
        self._watchers.append(
            asyncio.create_task(self._process_filesystem_events())
        )
        
        logger.info("Watchers initialized")
    
    async def _load_pending_work(self):
        """Load pending work from database queues"""
        logger.info("Loading pending work...")
        
        if not self.registry:
            return
        
        try:
            # Load pending schema proposals
            pending_schemas = self.registry.query_rows(
                'memory_schema_proposals',
                filters={'status': 'pending'},
                limit=100
            )
            
            for schema in pending_schemas:
                await self.schema_queue.put({
                    'type': 'schema_proposal',
                    'data': schema.dict() if hasattr(schema, 'dict') else dict(schema)
                })
            
            logger.info(f"Loaded {len(pending_schemas)} pending schemas")
            
            # Load files needing ingestion
            pending_files = self.registry.query_rows(
                'memory_documents',
                filters={'ingestion_status': 'pending'},
                limit=100
            )
            
            for file_doc in pending_files:
                await self.ingestion_queue.put({
                    'type': 'ingest_file',
                    'data': file_doc.dict() if hasattr(file_doc, 'dict') else dict(file_doc)
                })
            
            logger.info(f"Loaded {len(pending_files)} files for ingestion")
            
        except Exception as e:
            logger.error(f"Error loading pending work: {e}")
    
    async def _coordinator_loop(self):
        """Main coordination loop - processes queues and spawns agents"""
        logger.info("Starting coordinator loop...")
        
        while self._running:
            try:
                # Update heartbeat
                self.last_heartbeat = datetime.utcnow()
                
                # Skip if paused
                if self.status.value == 'paused':
                    await asyncio.sleep(1)
                    continue
                
                # Check agent capacity
                active_count = len(self._sub_agents)
                max_agents = self.config.get('max_concurrent_agents', 5)
                
                # Calculate available slots per queue type
                max_schema_agents = self.config.get('max_schema_agents', 2)
                max_ingestion_agents = self.config.get('max_ingestion_agents', 3)
                max_trust_agents = self.config.get('max_trust_agents', 2)
                
                schema_agents = sum(1 for a in self._sub_agents.values() if a.get('type') == 'schema_scout')
                ingestion_agents = sum(1 for a in self._sub_agents.values() if a.get('type') == 'ingestion_runner')
                trust_agents = sum(1 for a in self._sub_agents.values() if a.get('type') == 'trust_auditor')
                
                # Process schema queue (highest priority) - spawn multiple if available
                while (not self.schema_queue.empty() and 
                       schema_agents < max_schema_agents and 
                       active_count < max_agents):
                    item = await self.schema_queue.get()
                    await self.spawn_agent('schema_scout', item, priority='high')
                    schema_agents += 1
                    active_count += 1
                
                # Process ingestion queue - spawn multiple concurrently
                while (not self.ingestion_queue.empty() and 
                       ingestion_agents < max_ingestion_agents and 
                       active_count < max_agents):
                    item = await self.ingestion_queue.get()
                    await self.spawn_agent('ingestion_runner', item, priority='normal')
                    ingestion_agents += 1
                    active_count += 1
                
                # Process trust audit queue
                while (not self.trust_audit_queue.empty() and 
                       trust_agents < max_trust_agents and 
                       active_count < max_agents):
                    item = await self.trust_audit_queue.get()
                    await self.spawn_agent('trust_auditor', item, priority='normal')
                    trust_agents += 1
                    active_count += 1
                
                # Periodic trust audit
                if await self._should_run_trust_audit():
                    await self.schedule_trust_audit()
                
                # Wait before next iteration
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                logger.info("Coordinator loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in coordinator loop: {e}")
                self.metrics['errors'] += 1
                await asyncio.sleep(5)
    
    async def _create_agent(self, agent_type: str, agent_id: str, task_data: Dict) -> Any:
        """Create a sub-agent instance"""
        try:
            # Dynamically import agent class
            module_path = self.agent_types.get(agent_type)
            if not module_path:
                logger.error(f"Unknown agent type: {agent_type}")
                return None
            
            # For now, create a simple agent wrapper
            # In production, import the actual agent classes
            agent = SimpleAgent(
                agent_id=agent_id,
                agent_type=agent_type,
                task_data=task_data,
                registry=self.registry,
                kernel=self
            )
            
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create agent {agent_type}: {e}")
            return None
    
    async def _cleanup(self):
        """Cleanup resources on shutdown"""
        logger.info("Cleaning up Librarian kernel...")
        
        # Stop filesystem observer
        if self.fs_observer:
            self.fs_observer.stop()
            self.fs_observer.join()
        
        # Clear queues
        while not self.schema_queue.empty():
            self.schema_queue.get_nowait()
        while not self.ingestion_queue.empty():
            self.ingestion_queue.get_nowait()
        while not self.trust_audit_queue.empty():
            self.trust_audit_queue.get_nowait()
        
        logger.info("Cleanup complete")
    
    async def _process_filesystem_events(self):
        """Process filesystem events from watcher"""
        while self._running:
            try:
                if self.fs_handler:
                    event = await asyncio.wait_for(
                        self.fs_handler.queue.get(),
                        timeout=1.0
                    )
                    
                    await self._handle_filesystem_event(event)
                    
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing filesystem event: {e}")
    
    async def _handle_filesystem_event(self, event: Dict):
        """Handle a filesystem event"""
        event_type = event.get('type')
        file_path = event.get('path')
        is_book = event.get('is_book', False)
        file_type = event.get('file_type', '')
        
        logger.info(f"Filesystem event: {event_type} - {file_path} (book={is_book})")
        
        if event_type == 'file_created':
            # Queue for schema inference
            await self.schema_queue.put({
                'type': 'new_file',
                'path': file_path,
                'timestamp': event.get('timestamp'),
                'is_book': is_book,
                'file_type': file_type
            })
            
            # If it's a book, prioritize it for book ingestion pipeline
            if is_book:
                await self.ingestion_queue.put({
                    'type': 'book_ingestion',
                    'path': file_path,
                    'pipeline': 'book_ingestion',
                    'priority': 'high',
                    'timestamp': event.get('timestamp')
                })
                
                logger.info(f"Book detected, queued for specialized ingestion: {file_path}")
            
            await self._emit_event('file.created', {
                'path': file_path,
                'queued_for_processing': True,
                'is_book': is_book
            })
        
        elif event_type == 'file_modified':
            # Check if needs re-ingestion
            await self._emit_event('file.modified', {'path': file_path})
        
        elif event_type == 'file_deleted':
            # Update metadata
            await self._emit_event('file.deleted', {'path': file_path})
    
    async def _should_run_trust_audit(self) -> bool:
        """Check if it's time to run periodic trust audit"""
        # Implementation: check last audit time vs interval
        return False  # Placeholder
    
    async def schedule_trust_audit(self):
        """Schedule a trust audit job"""
        await self.trust_audit_queue.put({
            'type': 'periodic_audit',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        logger.info("Trust audit scheduled")
    
    async def submit_schema_proposal(self, schema_data: Dict):
        """Submit a schema proposal to Unified Logic"""
        await self.schema_queue.put({
            'type': 'schema_proposal',
            'data': schema_data
        })
    
    async def queue_ingestion(self, file_path: str, metadata: Dict = None):
        """Queue a file for ingestion"""
        await self.ingestion_queue.put({
            'type': 'ingest_file',
            'path': file_path,
            'metadata': metadata or {}
        })
    
    def get_queue_status(self) -> Dict[str, int]:
        """Get current queue depths"""
        return {
            'schema_queue': self.schema_queue.qsize(),
            'ingestion_queue': self.ingestion_queue.qsize(),
            'trust_audit_queue': self.trust_audit_queue.qsize()
        }


class SimpleAgent:
    """
    Simple agent wrapper for executing tasks.
    In production, replace with actual agent implementations.
    """
    
    def __init__(self, agent_id: str, agent_type: str, task_data: Dict, registry=None, kernel=None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.task_data = task_data
        self.registry = registry
        self.kernel = kernel
    
    async def execute(self) -> Dict:
        """Execute the agent's task"""
        logger.info(f"Agent {self.agent_id} ({self.agent_type}) executing task")
        
        try:
            # Simulate work
            await asyncio.sleep(2)
            
            # Log to memory_sub_agents
            if self.registry:
                try:
                    self.registry.insert_row('memory_execution_logs', {
                        'agent_id': self.agent_id,
                        'agent_type': self.agent_type,
                        'task_type': self.task_data.get('type'),
                        'status': 'completed',
                        'executed_at': datetime.utcnow().isoformat(),
                        'result': {'success': True}
                    })
                except Exception as e:
                    logger.warning(f"Could not log execution: {e}")
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'task_type': self.task_data.get('type')
            }
            
        except Exception as e:
            logger.error(f"Agent {self.agent_id} failed: {e}")
            raise
    
    async def stop(self):
        """Stop the agent"""
        logger.info(f"Stopping agent {self.agent_id}")
