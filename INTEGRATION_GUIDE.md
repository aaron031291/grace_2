# Quick Integration Guide

## Adding Trusted Sources Panel to Memory Studio

### Option 1: Add to MemoryStudioPanel tabs

Edit `frontend/src/panels/MemoryStudioPanel.tsx`:

```typescript
import { TrustedSourcesPanel } from './TrustedSourcesPanel';

// Add to view state options
const [view, setView] = useState<'workspace' | 'schema' | 'alerts' | 'sources'>('workspace');

// Add tab button
<button onClick={() => setView('sources')}>
  <Shield className="w-4 h-4" />
  Trusted Sources
</button>

// Add view rendering
{view === 'sources' && <TrustedSourcesPanel />}
```

### Option 2: Add to MemoryHubPanel

Edit `frontend/src/panels/MemoryHubPanel.tsx`:

```typescript
import { TrustedSourcesPanel } from './TrustedSourcesPanel';

// Add to sections
<button onClick={() => setActiveSection('sources')}>
  Sources
</button>

{activeSection === 'sources' && <TrustedSourcesPanel />}
```

### Option 3: Standalone Route

Add to your routing configuration:

```typescript
import TrustedSourcesPanel from './panels/TrustedSourcesPanel';

<Route path="/sources" element={<TrustedSourcesPanel />} />
```

---

## Testing the Implementation

### 1. Test Schema Inference on Upload

```bash
# Upload a file via the UI
# Check logs for:
"Schema inference queued: True"

# Check memory_insights table for new entry
# SQL: SELECT * FROM memory_insights WHERE insight_type='file_upload';
```

### 2. Test Breadcrumb Navigation

- Click on a folder in the file tree
- Verify breadcrumb shows: Root › folder
- Click "Root" to navigate back
- Verify currentPath updates

### 3. Test Trusted Sources

```bash
# Via UI:
1. Navigate to Trusted Sources panel
2. Click "Add Source"
3. Fill form:
   - Name: "Test Source"
   - Type: "website"
   - URL: "https://example.com/*"
   - Domains: "test"
4. Submit
5. Verify appears in "Pending" filter
6. Click "Approve"
7. Verify moves to "Active" filter
```

### 4. Test Source Validation

```python
# Backend console/test:
from backend.memory_tables.registry import table_registry
from backend.memory_tables.trusted_sources_integration import TrustedSourcesValidator

validator = TrustedSourcesValidator(table_registry)
result = validator.is_source_trusted("https://example.com/page", "test")
print(result)
# Should show: {'trusted': True, 'trust_score': 0.0, ...}
```

---

## Running the Schema Loader

```bash
# Generate ORM models for new schema
cd backend/memory_tables
python schema_loader.py

# Or if you have a specific command:
python -m backend.memory_tables.schema_loader
```

---

## API Endpoints Available

### Trusted Sources:
- `GET /api/memory/tables/memory_trusted_sources/rows` - List all
- `POST /api/memory/tables/memory_trusted_sources/rows` - Create
- `PATCH /api/memory/tables/memory_trusted_sources/rows/{id}` - Update
- `DELETE /api/memory/tables/memory_trusted_sources/rows/{id}` - Delete

### File Operations:
- `POST /api/memory/files/upload` - Upload with schema inference
- `GET /api/memory/tables/linked?file_path={path}` - Get linked rows

---

## Environment Variables (if needed)

```bash
# Add to .env if using external schema inference API
SCHEMA_INFERENCE_ENABLED=true
SCHEMA_INFERENCE_AUTO_APPROVE=false
TRUSTED_SOURCES_AUTO_INGEST=true
```

---

## Troubleshooting

### Schema inference not triggering:
- Check `BackgroundTasks` is passed to endpoint
- Verify `schema_agent.py` is accessible
- Check logs for errors in `_trigger_schema_inference()`

### Trusted sources not loading:
- Run schema loader to generate ORM model
- Verify table exists: `SELECT * FROM memory_trusted_sources;`
- Check API endpoint is accessible

### Breadcrumbs not showing:
- Verify `Breadcrumbs` component is imported
- Check `currentPath` state is initialized
- Ensure `onNavigate` prop is passed

---

## Next Development Steps

1. **Add file content viewer** in MemoryPanel file details
2. **Create trust metrics dashboard** showing aggregate stats
3. **Build sub-agent** for automated source curation
4. **Add trust indicators** as badges in file tree
5. **Implement conflict detection** when sources contradict
6. **Create derived table** for trust reports by domain

---

## Performance Considerations

- Trusted sources cache refreshes every 5 minutes
- Schema inference runs in background (non-blocking)
- File tree lazy-loads children on expand
- Table rows paginated (limit: 1000)

---

## Security Notes

- All source proposals start as "pending"
- Manual approval required for high-trust operations
- Trust scores recalculate on each ingestion
- Governance stamps track all approvals
- Contradiction detection flags suspicious sources
