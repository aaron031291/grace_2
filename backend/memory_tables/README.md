# Grace Memory Tables

**Self-building, intelligent knowledge storage for autonomous learning**

---

## Overview

Memory Tables is Grace's structured knowledge platform that automatically analyzes files, creates appropriate database schemas, and populates them with extracted metadata—all routed through governed workflows.

## Quick Start

```python
from backend.memory_tables.registry import table_registry
from backend.memory_tables.schema_agent import SchemaInferenceAgent

# Initialize
await table_registry.load_all_schemas()
await table_registry.initialize_database()

# Analyze a file
agent = SchemaInferenceAgent(registry=table_registry)
analysis = await agent.analyze_file(Path("document.pdf"))
proposal = await agent.propose_schema(analysis, table_registry.list_tables())

# Insert data
row_data = await agent.extract_row_data(Path("document.pdf"), proposal['table_name'])
table_registry.insert_row(proposal['table_name'], row_data)
```

## Components

### `registry.py`
Schema registry and database operations
- Load YAML schemas
- Generate SQLModel classes dynamically
- CRUD operations
- Database initialization

### `schema_agent.py`
LLM-powered schema inference
- File analysis
- Feature extraction
- Table selection
- Row data generation

### `content_pipeline.py`
Multi-format content extractors
- DocumentExtractor (text, PDF, markdown)
- CodeExtractor (Python, JS, TS, etc.)
- DatasetExtractor (CSV, JSON)
- MediaExtractor (audio, video, images)

### `initialization.py`
Startup integration
- Auto-load schemas
- Initialize database
- Register with clarity

### `models.py`
Base model classes

## Schemas

Pre-built schemas in `schema/`:
- `documents.yaml` - Books, reports, articles
- `codebases.yaml` - Code repositories
- `datasets.yaml` - Structured data
- `media.yaml` - Audio, video, images
- `insights.yaml` - LLM outputs

## API

Routes in `/api/memory/tables/`:
- `GET /` - List tables
- `GET /{name}/schema` - Get schema
- `GET /{name}/rows` - Query rows
- `POST /{name}/rows` - Insert row
- `POST /analyze` - Analyze file
- `POST /schemas` - Create schema
- `POST /ingest/{name}` - Ingest file

## Integration

### Unified Logic Hub
All operations route through governance:
```python
update_result = await unified_logic_hub.submit_update(
    update_type="memory_table_insert",
    component_targets=["memory_tables"],
    content={"table": "memory_documents", "data": row_data},
    risk_level="low"
)
```

### Clarity Framework
Tables auto-register as components and emit events

### Memory Fusion
Rows sync to long-term storage with versioning

## Usage Examples

### Analyze and Ingest
```bash
curl -X POST http://localhost:8001/api/memory/tables/analyze \
  -d '{"file_path": "training_data/doc.pdf"}'

curl -X POST "http://localhost:8001/api/memory/tables/ingest/memory_documents?file_path=training_data/doc.pdf"
```

### Query Data
```bash
curl "http://localhost:8001/api/memory/tables/memory_documents/rows?limit=50"
```

### Create Custom Schema
```bash
curl -X POST http://localhost:8001/api/memory/tables/schemas \
  -d '{
    "table_name": "memory_strategies",
    "fields": [...],
    "description": "Business strategies"
  }'
```

## Extension

### Add New Table Type
1. Create `schema/my_table.yaml`
2. Define fields, indexes
3. Restart → Auto-created

### Add Custom Extractor
```python
class MyExtractor:
    async def extract(self, file_path: Path):
        return {"field": "value"}

content_pipeline.extractors['my_type'] = MyExtractor()
```

## Documentation

See root-level docs:
- `MEMORY_TABLES_COMPLETE.md` - Full specification
- `MEMORY_TABLES_QUICKSTART.md` - User guide
- `MEMORY_TABLES_INTEGRATION.md` - Integration details
- `MEMORY_TABLES_SETUP.md` - Installation

## Dependencies

```bash
pip install sqlmodel>=0.0.14 sqlalchemy>=2.0.0 pyyaml>=6.0
```

Or add to `pyproject.toml` (already done).

## Status

✅ Production ready  
✅ Fully documented  
✅ Integrated with orchestrator  
🔄 UI components in progress  
🔄 Advanced extractors in progress  

---

**Version:** 1.0.0  
**Maintained by:** Grace Core Team  
**License:** MIT
