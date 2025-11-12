#!/usr/bin/env python3
"""
Memory Tables Schema Registry
Loads YAML schemas and generates SQLModel classes dynamically
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Type
from datetime import datetime
import uuid
from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import Column, DateTime, JSON, Text, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID

logger = logging.getLogger(__name__)


class SchemaRegistry:
    """
    Registry for memory table schemas
    Loads YAML definitions and generates SQLModel classes
    """
    
    def __init__(self, schema_dir: Path = None):
        self.schema_dir = schema_dir or Path("backend/memory_tables/schema")
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.models: Dict[str, Type[SQLModel]] = {}
        self.engine = None
        
    def load_all_schemas(self) -> int:
        """Load all YAML schema files from the schema directory"""
        count = 0
        
        if not self.schema_dir.exists():
            logger.warning(f"Schema directory not found: {self.schema_dir}")
            return count
        
        for schema_file in self.schema_dir.glob("*.yaml"):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema = yaml.safe_load(f)
                
                table_name = schema.get('table')
                if table_name:
                    self.schemas[table_name] = schema
                    logger.info(f"Loaded schema: {table_name}")
                    count += 1
                    
            except Exception as e:
                logger.error(f"Failed to load schema {schema_file}: {e}")
        
        return count
    
    def get_schema(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get schema definition by table name"""
        return self.schemas.get(table_name)
    
    def list_tables(self) -> List[str]:
        """List all registered table names"""
        return list(self.schemas.keys())
    
    def create_model_class(self, table_name: str) -> Optional[Type[SQLModel]]:
        """
        Dynamically create a SQLModel class from schema definition
        """
        schema = self.get_schema(table_name)
        if not schema:
            logger.error(f"Schema not found: {table_name}")
            return None
        
        # Build field definitions
        field_defs = {}
        
        for field_spec in schema.get('fields', []):
            field_name = field_spec['name']
            field_type = field_spec['type']
            
            # Map YAML types to Python types
            python_type = self._map_type(field_type)
            
            # Build Field kwargs
            field_kwargs = {}
            
            if field_spec.get('primary_key'):
                field_kwargs['primary_key'] = True
            
            if field_spec.get('unique'):
                field_kwargs['unique'] = True
            
            if field_spec.get('nullable', False):
                field_kwargs['nullable'] = True
            
            if 'default' in field_spec:
                field_kwargs['default'] = field_spec['default']
            elif field_spec.get('generated') and field_type == 'uuid':
                field_kwargs['default_factory'] = uuid.uuid4
            
            # Create the field
            if field_spec.get('primary_key') and field_type == 'uuid':
                field_defs[field_name] = (
                    Optional[uuid.UUID],
                    Field(default_factory=uuid.uuid4, **{k: v for k, v in field_kwargs.items() if k != 'default_factory'})
                )
            elif field_spec.get('nullable'):
                field_defs[field_name] = (Optional[python_type], Field(None, **field_kwargs))
            else:
                field_defs[field_name] = (python_type, Field(**field_kwargs))
        
        # Create the class dynamically
        model_class = type(
            table_name.title().replace('_', ''),
            (SQLModel,),
            {
                '__tablename__': table_name,
                '__table_args__': {'extend_existing': True},
                **field_defs
            }
        )
        
        self.models[table_name] = model_class
        logger.info(f"Created model class: {table_name}")
        return model_class
    
    def _map_type(self, yaml_type: str) -> type:
        """Map YAML type strings to Python types"""
        type_map = {
            'uuid': uuid.UUID,
            'string': str,
            'text': str,
            'integer': int,
            'float': float,
            'boolean': bool,
            'datetime': datetime,
            'json': dict,
        }
        return type_map.get(yaml_type, str)
    
    def initialize_database(self, db_url: str = "sqlite:///databases/memory_tables.db"):
        """Initialize database and create all tables"""
        self.engine = create_engine(db_url, echo=False)
        
        # Create all models first
        for table_name in self.schemas:
            self.create_model_class(table_name)
        
        # Create tables
        SQLModel.metadata.create_all(self.engine)
        logger.info(f"Database initialized: {db_url}")
    
    def get_model(self, table_name: str) -> Optional[Type[SQLModel]]:
        """Get the SQLModel class for a table"""
        if table_name not in self.models:
            self.create_model_class(table_name)
        return self.models.get(table_name)
    
    def insert_row(self, table_name: str, data: Dict[str, Any]) -> Optional[Any]:
        """Insert a row into a table"""
        model = self.get_model(table_name)
        if not model or not self.engine:
            return None
        
        try:
            with Session(self.engine) as session:
                instance = model(**data)
                session.add(instance)
                session.commit()
                session.refresh(instance)
                return instance
        except Exception as e:
            logger.error(f"Failed to insert row into {table_name}: {e}")
            return None
    
    def query_rows(self, table_name: str, filters: Dict[str, Any] = None, limit: int = 100) -> List[Any]:
        """Query rows from a table"""
        model = self.get_model(table_name)
        if not model or not self.engine:
            return []
        
        try:
            with Session(self.engine) as session:
                stmt = select(model)
                
                # Apply filters if provided
                if filters:
                    for key, value in filters.items():
                        if hasattr(model, key):
                            stmt = stmt.where(getattr(model, key) == value)
                
                stmt = stmt.limit(limit)
                results = session.exec(stmt).all()
                return list(results)
        except Exception as e:
            logger.error(f"Failed to query {table_name}: {e}")
            return []
    
    def update_row(self, table_name: str, row_id: uuid.UUID, updates: Dict[str, Any]) -> bool:
        """Update a row in a table"""
        model = self.get_model(table_name)
        if not model or not self.engine:
            return False
        
        try:
            with Session(self.engine) as session:
                stmt = select(model).where(model.id == row_id)
                row = session.exec(stmt).first()
                
                if row:
                    for key, value in updates.items():
                        if hasattr(row, key):
                            setattr(row, key, value)
                    session.add(row)
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to update row in {table_name}: {e}")
            return False
    
    def propose_schema(self, table_name: str, fields: List[Dict[str, Any]], description: str = "") -> Dict[str, Any]:
        """
        Create a schema proposal (for LLM-driven schema creation)
        Returns a schema dict that can be saved as YAML
        """
        return {
            'table': table_name,
            'description': description,
            'fields': fields,
            'indexes': [],
            'proposed_at': datetime.now().isoformat(),
            'status': 'proposed'
        }
    
    def save_schema(self, schema: Dict[str, Any]) -> bool:
        """Save a schema definition to YAML file"""
        table_name = schema.get('table')
        if not table_name:
            return False
        
        try:
            schema_file = self.schema_dir / f"{table_name}.yaml"
            self.schema_dir.mkdir(parents=True, exist_ok=True)
            
            with open(schema_file, 'w', encoding='utf-8') as f:
                yaml.dump(schema, f, default_flow_style=False, sort_keys=False)
            
            # Reload the schema
            self.schemas[table_name] = schema
            logger.info(f"Saved schema: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save schema {table_name}: {e}")
            return False


# Global registry instance
table_registry = SchemaRegistry()
