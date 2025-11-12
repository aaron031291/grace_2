#!/usr/bin/env python3
"""
Memory Tables Initialization
Loads schemas and sets up database on startup
"""

import logging
from pathlib import Path
from .registry import table_registry

logger = logging.getLogger(__name__)


async def initialize_memory_tables(db_url: str = None) -> bool:
    """
    Initialize the memory tables system
    - Load all schemas
    - Create database tables
    - Register with clarity
    """
    try:
        logger.info("🗄️ Initializing Memory Tables system...")
        
        # Load schemas
        schema_count = table_registry.load_all_schemas()
        logger.info(f"✅ Loaded {schema_count} table schemas")
        
        # Initialize database
        if not db_url:
            # Default to SQLite in databases folder
            db_path = Path("databases/memory_tables.db")
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db_url = f"sqlite:///{db_path}"
        
        table_registry.initialize_database(db_url)
        logger.info(f"✅ Database initialized: {db_url}")
        
        # Log table summary
        tables = table_registry.list_tables()
        logger.info(f"📊 Active tables: {', '.join(tables)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Memory Tables initialization failed: {e}")
        return False


async def register_with_clarity():
    """Register memory tables with clarity manifest"""
    try:
        from backend.clarity_manifest import clarity_manifest
        
        # Register each table as a clarity component
        for table_name in table_registry.list_tables():
            schema = table_registry.get_schema(table_name)
            
            await clarity_manifest.register_component(
                component_id=f"memory_table_{table_name}",
                component_type="memory_table",
                metadata={
                    'table_name': table_name,
                    'description': schema.get('description', ''),
                    'field_count': len(schema.get('fields', [])),
                    'status': 'active'
                }
            )
        
        logger.info("✅ Memory tables registered with clarity")
        return True
        
    except Exception as e:
        logger.warning(f"Could not register with clarity: {e}")
        return False
