# Memory Tables - Quick Start Guide

## 🚀 Using Grace's Self-Building Memory System

### 1. Analyze a File

```bash
curl -X POST http://localhost:8001/api/memory/tables/analyze \
  -H "Content-Type: application/json" \
  -d '{"file_path": "training_data/my_document.pdf"}'
```

**Response:**
```json
{
  "success": true,
  "file_path": "training_data/my_document.pdf",
  "analysis": {
    "detected_type": "document",
    "features": {
      "estimated_tokens": 5000,
      "has_title": true
    }
  },
  "proposal": {
    "action": "use_existing",
    "table_name": "memory_documents",
    "confidence": 0.9,
    "reason": "File type 'document' matches existing table"
  }
}
```

### 2. Ingest File into Table

```bash
curl -X POST "http://localhost:8001/api/memory/tables/ingest/memory_documents?file_path=training_data/my_document.pdf"
```

**Response:**
```json
{
  "success": true,
  "table": "memory_documents",
  "file_path": "training_data/my_document.pdf",
  "row_id": "a3f1e2c4-...",
  "update_id": "upd_123"
}
```

### 3. Query Table Data

```bash
curl "http://localhost:8001/api/memory/tables/memory_documents/rows?limit=10"
```

**Response:**
```json
{
  "success": true,
  "table": "memory_documents",
  "rows": [
    {
      "id": "a3f1e2c4-...",
      "file_path": "training_data/my_document.pdf",
      "title": "My Document",
      "source_type": "custom",
      "token_count": 5000,
      "trust_score": 0.0,
      "risk_level": "low"
    }
  ],
  "count": 1
}
```

### 4. List All Tables

```bash
curl http://localhost:8001/api/memory/tables/
```

**Response:**
```json
{
  "success": true,
  "tables": [
    {
      "name": "memory_documents",
      "description": "Structured metadata for textual knowledge assets",
      "field_count": 16,
      "status": "active"
    },
    {
      "name": "memory_codebases",
      "description": "Metadata for imported repositories",
      "field_count": 11,
      "status": "active"
    }
  ],
  "count": 5
}
```

### 5. Get Schema Details

```bash
curl http://localhost:8001/api/memory/tables/memory_documents/schema
```

### 6. Create Custom Schema (Advanced)

```bash
curl -X POST http://localhost:8001/api/memory/tables/schemas \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "memory_strategies",
    "description": "Business strategy documents",
    "fields": [
      {"name": "id", "type": "uuid", "primary_key": true, "generated": true},
      {"name": "file_path", "type": "string", "unique": true, "required": true},
      {"name": "strategy_type", "type": "string"},
      {"name": "industry", "type": "string"},
      {"name": "key_metrics", "type": "json", "default": []}
    ],
    "confidence": 0.8,
    "reason": "Custom schema for strategy analysis"
  }'
```

---

## 🔄 Typical Workflow

### Scenario: Building E-commerce Intelligence

```python
import requests

base_url = "http://localhost:8001"

# 1. Upload market research
files = [
    "training_data/market_research_2024.pdf",
    "training_data/competitor_analysis.docx"
]

for file in files:
    # Analyze
    response = requests.post(f"{base_url}/api/memory/tables/analyze", 
                            json={"file_path": file})
    proposal = response.json()["proposal"]
    
    # Ingest
    requests.post(f"{base_url}/api/memory/tables/ingest/{proposal['table_name']}",
                 params={"file_path": file})

# 2. Upload code repositories
code_files = [
    "training_data/competitor_repo/",
]

for repo in code_files:
    requests.post(f"{base_url}/api/memory/tables/ingest/memory_codebases",
                 params={"file_path": repo})

# 3. Upload customer datasets
datasets = [
    "training_data/customer_purchases.csv",
    "training_data/demographics.json"
]

for dataset in datasets:
    requests.post(f"{base_url}/api/memory/tables/ingest/memory_datasets",
                 params={"file_path": dataset})

# 4. Query insights
# Get all documents about e-commerce
docs = requests.get(f"{base_url}/api/memory/tables/memory_documents/rows",
                   params={"filters": '{"source_type": "report"}'})

# Get customer datasets
data = requests.get(f"{base_url}/api/memory/tables/memory_datasets/rows")

# 5. Grace can now reason across all this data
# - Compare strategies from docs
# - Analyze code patterns
# - Find insights in customer data
```

---

## 📊 Python SDK Usage

```python
from pathlib import Path
from backend.memory_tables.registry import table_registry
from backend.memory_tables.schema_agent import SchemaInferenceAgent

# Initialize
await table_registry.load_all_schemas()
await table_registry.initialize_database()

agent = SchemaInferenceAgent(registry=table_registry)

# Analyze file
file_path = Path("training_data/business_plan.pdf")
analysis = await agent.analyze_file(file_path)
proposal = await agent.propose_schema(analysis, table_registry.list_tables())

# Extract and insert
if proposal['action'] == 'use_existing':
    row_data = await agent.extract_row_data(file_path, proposal['table_name'])
    table_registry.insert_row(proposal['table_name'], row_data)

# Query
rows = table_registry.query_rows('memory_documents', 
                                filters={'source_type': 'report'},
                                limit=50)
```

---

## 🎯 Grace's Autonomous Mode

When running in autonomous mode, Grace will:

1. **Monitor `training_data/` folder** for new files
2. **Analyze each file** automatically
3. **Propose schema** if needed (requires approval)
4. **Ingest data** into appropriate table
5. **Update trust scores** via clarity pipeline
6. **Sync to Memory Fusion** for long-term storage
7. **Log all operations** immutably

Enable with:
```bash
curl -X POST http://localhost:8001/api/autonomous/enable \
  -d '{"watch_folders": ["training_data"], "auto_ingest": true}'
```

---

## 🔒 Governance

All operations route through **Unified Logic Hub**:

- **Schema creation** → Medium risk, requires approval
- **Row insert** → Low risk, auto-approved
- **Bulk operations** → Medium risk, queued for review

Check pending approvals:
```bash
curl http://localhost:8001/api/unified-logic/pending
```

Approve operation:
```bash
curl -X POST http://localhost:8001/api/unified-logic/approve \
  -d '{"update_id": "upd_123"}'
```

---

## 📈 Statistics

```bash
curl http://localhost:8001/api/memory/tables/stats
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_tables": 5,
    "tables": [
      {
        "name": "memory_documents",
        "row_count": 47,
        "field_count": 16,
        "description": "Structured metadata for textual knowledge assets"
      }
    ]
  }
}
```

---

## 🚀 Next: Building Businesses

With structured memory, Grace can:

1. **Synthesize insights** across domains
2. **Detect contradictions** in strategy vs implementation
3. **Generate recommendations** based on data patterns
4. **Auto-create** new tables for emerging needs
5. **Build** data-driven business plans

Example:
```
User: "Build me an e-commerce recommendation engine"

Grace:
1. Queries memory_codebases for existing ML patterns
2. Queries memory_datasets for customer behavior data
3. Queries memory_documents for business requirements
4. Synthesizes into implementation plan
5. Generates code using learned patterns
6. Tests against customer data
7. Delivers working MVP
```

**All powered by self-built, structured memory.**
