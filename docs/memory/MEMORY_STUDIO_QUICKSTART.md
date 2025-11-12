# Memory Studio - Quick Start 🚀

## What Is Memory Studio?

Your Memory Workspace is now a **complete knowledge curation platform** with:
- 📁 **Workspace** - File management with drag & drop
- ⚙️ **Pipelines** - 6 automated processing workflows
- 📊 **Dashboard** - Real-time analytics and insights
- 🤖 **Grace AI** - Intelligent co-pilot for all content

---

## 🚀 Launch in 3 Steps

### Step 1: Restart Backend
```bash
# Stop current backend (Ctrl+C)
python -m uvicorn backend.main:app --reload --port 8000
```

Wait for: `Application startup complete`

### Step 2: Restart Frontend
```bash
cd frontend
npm run dev
```

Wait for: `Local:   http://localhost:5173/`

### Step 3: Open Memory Studio
1. Go to http://localhost:5173
2. Login: admin / admin123
3. Click "📁 Memory" button

---

## 🎯 Try These Features (2 Minutes)

### Feature 1: Upload & Process (30 seconds)
```
1. Click "Workspace" tab (default view)
2. Drag a .txt file onto the panel
3. Click on the file in tree
4. Notice auto-metadata in footer
5. Metadata shows: #text #readable #document
```

### Feature 2: View Pipelines (30 seconds)
```
1. Click "Pipelines" tab
2. See 6 available pipelines:
   - Text to Embeddings
   - PDF Extraction  
   - Code Analysis
   - Audio Transcription
   - Image Vision
   - Batch Training
3. Each shows: stages, file types, output
```

### Feature 3: Start a Pipeline (30 seconds)
```
1. (With file uploaded from Feature 1)
2. In Pipelines view, click "Text to Embeddings"
3. See it processes through 6 stages
4. Watch progress bar fill to 100%
5. Job appears in "Active Jobs" panel
```

### Feature 4: View Analytics (30 seconds)
```
1. Click "Dashboard" tab
2. See metric cards:
   - Total Jobs: 1
   - Completed: 1
   - Running: 0
   - Success Rate: 100%
3. See Pipeline Usage chart
4. See Recent Jobs list
```

---

## 📋 Interface Overview

### 3 Main Tabs

**Workspace** (File Management)
- File tree on left
- Monaco editor on right
- Grace chat panel (optional)
- Drag & drop upload
- Auto-metadata generation

**Pipelines** (Processing Hub)
- Pipeline library (left panel)
- Active jobs (right panel)
- Real-time progress bars
- Status indicators
- Auto-refresh every 3s

**Dashboard** (Analytics)
- Metric cards (4 key metrics)
- Pipeline usage chart
- Recent jobs timeline
- Success/failure tracking

---

## 🎮 Keyboard & Mouse

### Navigation
- Click tabs to switch views
- Scroll in file tree
- Click files to select

### File Operations (Workspace)
- Drag files → Upload
- Click "Grace" → AI chat
- Click "Save" → Save file
- Click "Delete" → Remove file

### Pipeline Operations
- Click pipeline → See details
- Jobs auto-refresh → No action needed
- Progress bars → Live updates

---

## 🔥 Power Features

### 1. Auto-Pipeline Recommendation
```
Upload a file → System recommends best pipeline
- .txt → Text to Embeddings
- .pdf → PDF Extraction
- .py  → Code Analysis
- .mp3 → Audio Transcription
- .jpg → Image Vision
```

### 2. Intelligent Metadata
Every uploaded file gets:
```json
{
  "tags": ["type", "category"],
  "status": "uploaded",
  "grace_notes": ["Actionable insights"],
  "uploaded_at": "timestamp"
}
```

### 3. Pipeline Stages
All pipelines go through optimized stages:
```
Upload → Validate → Extract → Clean → 
Chunk → Embed → Index → Sync
```

### 4. Real-Time Monitoring
- Jobs update every 3 seconds
- Progress bars show completion %
- Status colors: Green (done), Blue (running), Red (failed)
- Timestamps show when started

---

## 💡 Use Cases

### Use Case 1: Build Training Dataset
```
1. Upload 50 text files (drag & drop)
2. Select all in Workspace
3. Run "Batch Training" pipeline
4. System prepares training dataset
5. Export for model fine-tuning
```

### Use Case 2: Process PDFs
```
1. Upload research papers (PDFs)
2. System recommends "PDF Extraction"
3. Run pipeline on all PDFs
4. Text extracted, chunked, embedded
5. Now searchable in Grace's memory
```

### Use Case 3: Index Codebase
```
1. Upload source files (.py, .js, .ts)
2. Run "Code Analysis" pipeline
3. Functions extracted & documented
4. Code becomes queryable
5. Ask Grace: "Find authentication code"
```

### Use Case 4: Transcribe Audio
```
1. Upload meeting recording (.mp3)
2. Run "Audio Transcription" pipeline
3. Whisper generates transcript
4. Text chunked and embedded
5. Search: "What was said about X?"
```

---

## 📊 Understanding the Dashboard

### Metric Card: Total Jobs
- Shows all jobs ever run
- Increases with each pipeline start
- Tracks historical activity

### Metric Card: Completed
- Successfully finished jobs
- Shows success rate %
- Green indicator = good health

### Metric Card: Running
- Currently active jobs
- Average progress shown
- Blue indicator = processing

### Metric Card: Failed
- Jobs that encountered errors
- Red indicator = needs attention
- Click to see error details (future)

### Pipeline Usage Chart
- Horizontal bars show job distribution
- Width = percentage of total jobs
- Helps identify popular pipelines

---

## 🐛 Troubleshooting

### Pipeline Not Showing?
- Refresh browser (Ctrl+R)
- Check backend is running
- Verify: http://localhost:8000/api/ingestion/pipelines

### Jobs Not Updating?
- Auto-refresh is 3 seconds
- Check network tab (F12) for errors
- Verify backend not crashed

### Upload Not Working?
- Check file size < 50MB
- Verify `grace_training/` folder exists
- Check backend logs for errors

### Dashboard Empty?
- Run at least one pipeline first
- Metrics need jobs to display
- Try uploading a file in Workspace

---

## ✅ Success Checklist

You know it's working when:

- [ ] Can switch between 3 tabs
- [ ] Workspace shows file tree
- [ ] Can drag & drop files
- [ ] Pipelines tab shows 6 pipelines
- [ ] Can start a pipeline
- [ ] Progress bar animates
- [ ] Job shows in Active Jobs
- [ ] Dashboard shows metrics
- [ ] Metric cards have numbers
- [ ] Pipeline usage chart displays

---

## 🎯 Next Steps

### After Basic Testing

1. **Upload More Files**
   - Try different file types
   - Test pipeline recommendations
   - Build your knowledge library

2. **Explore Pipelines**
   - Read pipeline descriptions
   - Understand stage workflows
   - Try each pipeline type

3. **Monitor Performance**
   - Check success rates
   - Identify bottlenecks
   - Optimize configurations

4. **Ask Grace**
   - Use chat in Workspace
   - Get AI insights on files
   - Build collaborative workflows

---

## 📞 Need Help?

### Documentation
- Full guide: [MEMORY_STUDIO_COMPLETE.md](file:///c:/Users/aaron/grace_2/MEMORY_STUDIO_COMPLETE.md)
- Hub features: [MEMORY_HUB_COMPLETE.md](file:///c:/Users/aaron/grace_2/MEMORY_HUB_COMPLETE.md)
- Original: [MEMORY_PANEL_COMPLETE.md](file:///c:/Users/aaron/grace_2/MEMORY_PANEL_COMPLETE.md)

### API Testing
```bash
# List pipelines
curl http://localhost:8000/api/ingestion/pipelines

# Get metrics
curl http://localhost:8000/api/ingestion/metrics

# List jobs
curl http://localhost:8000/api/ingestion/jobs
```

### Common Issues
1. 404 errors → Restart backend
2. Blank screen → Hard refresh (Ctrl+Shift+R)
3. No metrics → Run a pipeline first

---

**You're ready to curate Grace's knowledge like a pro!** 🎓

Start with the Workspace → Try a pipeline → Check the Dashboard → Watch the magic happen! ✨
