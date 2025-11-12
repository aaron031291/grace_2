# Memory Hub Quick Start 🚀

## What's New?
Your Memory Workspace is now an "Everything Hub" with:
- 📁 **Drag & Drop** - Drop files to upload
- 🤖 **Grace AI** - Ask questions about any file
- 🏷️ **Smart Tags** - Auto-categorization by file type
- 📊 **Metadata** - Track processing status
- 🎯 **Quick Actions** - Summarize, extract, improve

---

## 🚀 Get Started (3 Steps)

### Step 1: Restart Frontend
```bash
cd frontend
npm run dev
```

Wait for: `➜  Local:   http://localhost:5173/`

### Step 2: Open Memory Hub
1. Go to http://localhost:5173
2. Login: admin / admin123
3. Click "📁 Memory" button

### Step 3: Start Using!

**Upload a File:**
- Drag any file from desktop → Drop on Memory Hub
- Or click "↑ Upload" button

**Chat with Grace:**
- Click on a file in the tree
- Click "💬 Grace" button
- Ask: "Summarize this file"

---

## 🎯 Try These Features

### 1. Drag & Drop Upload
```
1. Open Memory Hub
2. Drag a text file from desktop
3. Drop anywhere on the panel
4. Watch upload progress bar
5. File appears in tree!
```

### 2. Ask Grace
```
1. Click on any text file
2. Click "💬 Grace" button (top right)
3. Click "Summarize" quick action
4. Grace reads the file and responds!
```

### 3. View Metadata
```
1. Upload a PDF or image
2. Look at the bottom footer
3. See auto-generated tags
4. Status shows processing needs
```

### 4. Multi-File Upload
```
1. Click "↑ Upload" button
2. Select multiple files (Ctrl+Click)
3. All upload with individual progress bars
4. Metadata auto-created for each
```

---

## 📋 Supported File Types

| Type | Extensions | Auto-Tags | What Happens |
|------|-----------|-----------|--------------|
| 📄 Documents | .pdf, .docx | `document`, `needs-extraction` | Flagged for text extraction |
| 💻 Code | .py, .js, .ts | `code`, `source` | Ready for analysis |
| 🖼️ Images | .jpg, .png | `image`, `needs-vision` | Flagged for vision AI |
| 🎵 Audio | .mp3, .wav | `audio`, `needs-transcription` | Flagged for Whisper |
| 🎬 Video | .mp4, .mov | `video`, `multimodal` | Flagged for processing |
| 📊 Data | .json, .yaml | `data`, `structured` | Ready for parsing |

---

## 💬 Grace Chat Examples

### Quick Actions (One Click)
- **Summarize** → "Give me a brief summary"
- **Key Points** → "List the main ideas"
- **Improve** → "How can I make this better?"
- **Questions** → "Create quiz questions"

### Custom Prompts (Type Anything)
- "What programming language is this?"
- "Extract all the URLs from this file"
- "Translate this to Spanish"
- "Find potential bugs in this code"
- "Convert this to markdown format"

---

## 🎨 Visual Guide

### Memory Hub Layout
```
┌──────────────┬────────────────────────┬─────────────┐
│  File Tree   │    Monaco Editor       │ Grace Chat  │
│  + Icons     │    (Code Editing)      │ (Optional)  │
├──────────────┼────────────────────────┴─────────────┤
│ 📁 docs      │ File: example.md                     │
│   📄 a.md    │ ┌─────────────────────────────────┐  │
│   🖼️ img.jpg │ │ # Hello World                   │  │
│ 📁 code      │ │ This is a markdown file...      │  │
│   🐍 x.py    │ └─────────────────────────────────┘  │
│              │ [💬 Grace] [💾 Save] [🗑️ Delete]    │
│ Status:      ├──────────────────────────────────────┤
│ 25 files     │ Tags: #document #text                │
│ 0.15 MB      │ ✓ Embedded  Ingested Nov 12         │
│              └──────────────────────────────────────┘
│ [+ File]
│ [+ Folder]
│ [↑ Upload]
│ [🔄]
└──────────────┘
```

---

## 🐛 Troubleshooting

### Memory Hub Not Showing?
```bash
# Restart frontend
cd frontend
npm run dev

# Hard refresh browser
Ctrl+Shift+R
```

### Upload Not Working?
- Check backend is running (port 8000)
- Check browser console (F12) for errors
- Verify file size < 50MB

### Grace Chat Not Responding?
- Check `/api/chat` endpoint exists
- Verify Grace LLM is configured
- Check backend logs for errors

---

## 📊 What Gets Created

### When You Upload a File
```
grace_training/
  └── myfile.pdf              ← Your file
      └── myfile.pdf.meta.json ← Auto-created metadata
```

### Metadata Example
```json
{
  "uploaded_at": "2024-11-12T20:30:00Z",
  "content_type": "application/pdf",
  "tags": ["document", "needs-extraction"],
  "grace_notes": ["Document uploaded - extraction pending"],
  "status": "needs_extraction"
}
```

---

## 🎯 Next Steps

Once you're comfortable with basics:

1. **Organize Files** - Create folders, move files around
2. **Batch Upload** - Drop entire folders worth of files
3. **Train Grace** - Upload training data for fine-tuning
4. **Collaborate** - Use Grace to understand complex docs
5. **Process Media** - Upload videos/audio for transcription

---

## 🔥 Power User Tips

### Keyboard Shortcuts
- `Ctrl+S` - Save file
- `Ctrl+F` - Find in file
- `F2` - Rename (coming soon)
- `Delete` - Delete file (with confirm)

### File Organization
```
grace_training/
  ├── training_data/      ← Training corpus
  ├── documents/          ← PDFs, docs
  ├── media/              ← Images, audio, video
  ├── code/               ← Source code
  └── exports/            ← Generated content
```

### Metadata Power
- Edit `.meta.json` files directly
- Add custom tags
- Track ingestion status
- Link files together

---

## ✅ Success Checklist

You know it's working when:

- [ ] Can drag & drop files
- [ ] Upload progress shows
- [ ] Files appear in tree with icons
- [ ] Can click Grace button
- [ ] Grace responds to questions
- [ ] Metadata shows in footer
- [ ] Can create new files/folders
- [ ] Can edit files in Monaco
- [ ] Auto-save works (dirty indicator)

---

## 🎉 You're Ready!

**The Memory Hub is now your:**
- 📚 Knowledge repository
- 🤖 AI collaboration space
- 📁 File management system
- 🎯 Training data organizer
- 💡 Intelligence hub

**Start uploading and let Grace help you manage everything!**

---

**Need Help?**
- Full docs: [MEMORY_HUB_COMPLETE.md](file:///c:/Users/aaron/grace_2/MEMORY_HUB_COMPLETE.md)
- Quick test: [TEST_MEMORY_PANEL.md](file:///c:/Users/aaron/grace_2/TEST_MEMORY_PANEL.md)
- Debug guide: [FRONTEND_DEBUG_STEPS.md](file:///c:/Users/aaron/grace_2/FRONTEND_DEBUG_STEPS.md)
