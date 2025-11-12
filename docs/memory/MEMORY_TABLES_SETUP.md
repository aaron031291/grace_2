# Memory Tables - Setup Instructions

## 📦 Installation

### 1. Install Dependencies

```bash
pip install sqlmodel>=0.0.14 sqlalchemy>=2.0.0 pyyaml>=6.0
```

Or add to your `pyproject.toml`:
```toml
[project]
dependencies = [
    "sqlmodel>=0.0.14",
    "sqlalchemy>=2.0.0",
    "pyyaml>=6.0",
    # ... other deps
]
```

### 2. Initialize Database

The system auto-initializes on first run:
```python
from backend.memory_tables.initialization import initialize_memory_tables

# Initialize with default SQLite database
await initialize_memory_tables()

# Or specify custom database
await initialize_memory_tables("postgresql://user:pass@localhost/grace")
```

### 3. Load Schemas

Schemas load automatically from `backend/memory_tables/schema/*.yaml`:
```python
from backend.memory_tables.registry import table_registry

count = table_registry.load_all_schemas()
print(f"Loaded {count} schemas")
```

### 4. Verify Installation

```bash
python -c "from backend.memory_tables.registry import table_registry; print('OK')"
```

---

## 🚀 Quick Start

### Using the API

Start Grace:
```bash
python backend/unified_grace_orchestrator.py
```

Test endpoints:
```bash
# List tables
curl http://localhost:8001/api/memory/tables/

# Analyze a file
curl -X POST http://localhost:8001/api/memory/tables/analyze \
  -H "Content-Type: application/json" \
  -d '{"file_path": "README.md"}'
```

### Using Python

```python
from pathlib import Path
from backend.memory_tables.registry import table_registry
from backend.memory_tables.schema_agent import SchemaInferenceAgent

# Setup
await table_registry.load_all_schemas()
await table_registry.initialize_database()

agent = SchemaInferenceAgent(registry=table_registry)

# Analyze and ingest
file_path = Path("training_data/document.pdf")
analysis = await agent.analyze_file(file_path)
proposal = await agent.propose_schema(analysis, table_registry.list_tables())

if proposal['action'] == 'use_existing':
    row_data = await agent.extract_row_data(file_path, proposal['table_name'])
    table_registry.insert_row(proposal['table_name'], row_data)
```

---

## 🗂️ File Structure

```
backend/memory_tables/
├── __init__.py                 # Package exports
├── registry.py                 # Schema registry & DB operations
├── models.py                   # Base model classes
├── schema_agent.py             # LLM schema inference
├── content_pipeline.py         # File analysis extractors
├── initialization.py           # Startup integration
├── requirements.txt            # Dependencies
└── schema/                     # YAML schema definitions
    ├── documents.yaml
    ├── codebases.yaml
    ├── datasets.yaml
    ├── media.yaml
    └── insights.yaml

backend/routes/
└── memory_tables_api.py        # FastAPI routes
```

---

## 🔧 Configuration

### Database URL

Default: `sqlite:///databases/memory_tables.db`

Override via environment:
```bash
export MEMORY_TABLES_DB_URL="postgresql://localhost/grace_memory"
```

Or in code:
```python
await initialize_memory_tables(
    db_url="postgresql://user:pass@localhost/grace"
)
```

### Schema Directory

Default: `backend/memory_tables/schema/`

Override:
```python
from backend.memory_tables.registry import SchemaRegistry

registry = SchemaRegistry(schema_dir=Path("custom/schemas"))
registry.load_all_schemas()
```

---

## ✅ Verification Checklist

- [ ] Dependencies installed (`sqlmodel`, `pyyaml`)
- [ ] Database directory exists (`databases/`)
- [ ] Schemas loaded (5 tables: documents, codebases, datasets, media, insights)
- [ ] API routes registered in orchestrator
- [ ] `/api/memory/tables/` endpoint responds
- [ ] Can analyze a file successfully
- [ ] Can insert a row successfully

---

## 🔍 Troubleshooting

### "No module named 'sqlmodel'"
```bash
pip install sqlmodel
```

### "Table already exists" error
The system uses `extend_existing=True`, so this is normal. Ignore or drop tables:
```python
from sqlmodel import SQLModel
SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)
```

### Schema not loading
Check:
1. YAML files exist in `backend/memory_tables/schema/`
2. YAML is valid (use `yamllint` or online validator)
3. File permissions (readable)

### Import errors in orchestrator
The orchestrator uses safe imports with fallbacks. Check logs:
```python
from backend.unified_grace_orchestrator import import_errors
print(import_errors)
```

---

## 📚 Next Steps

1. **Read** [MEMORY_TABLES_QUICKSTART.md](MEMORY_TABLES_QUICKSTART.md)
2. **Review** [MEMORY_TABLES_INTEGRATION.md](MEMORY_TABLES_INTEGRATION.md)
3. **Try** the API examples
4. **Create** custom schemas for your domain
5. **Build** on the foundation

---

**Support:** Check logs in `logs/orchestrator.log`  
**Documentation:** See `MEMORY_TABLES_*.md` files  
**Status:** Production ready, actively maintained
