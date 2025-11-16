# Memory Explorer (UI Spec)

## Goal
Give operators a simple file-explorer style view into Grace’s RAG memory so they can:
- Browse existing artifacts (docs, recordings, transcripts, voice notes)
- Inspect metadata (source, tags, ingestion date, embedding status)
- Upload/add new data directly into the vector store/world model
- Re-ingest or update artifacts when source files change

## Layout
1. **Sidebar Tree / Filters**
   - Categories: knowledge artifacts, recordings, documents, retrospectives, mission outcomes
   - Filters for domain, tags, ingestion date, embedding status

2. **Artifact List**
   - Columns: name/source, type, tags, last updated, embeddings indexed?, missions referencing it
   - Search bar (RAG query) to find content quickly

3. **Preview & Actions Pane**
   - Shows snippet/summary, metadata, linked missions/outcomes
   - Actions: preview full text, download original, re-ingest, open in workspace, delete (with governance)

4. **Upload / Ingest Controls**
   - Drag-drop area or “Add knowledge” button
   - Options: upload file, paste text, link remote source, attach voice note
   - On submit, calls existing ingestion endpoints and immediately shows status (chunking, embedding, indexing)

## Data Sources / APIs
- `vector_integration` database (VectorEmbedding, KnowledgeArtifact tables)
- Recording pipeline / transcripts
- `/api/remote-access/rag/ingest-text` for quick text additions
- Document ingestion services for files / bulk uploads
- World model entries for mission outcomes/retrospectives

## Integration Notes
- Reuse dynamic workspaces: selecting an artifact can open a pop-out tab with deeper context (mission references, KPI impacts).
- Governance: destructive actions (delete, overwrite) should trigger approval flow.
- Logging: every upload/re-ingest event should publish to trigger mesh for audit and to kick off any auto-embedding jobs.
