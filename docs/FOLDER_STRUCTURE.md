# 📁 Grace Repository Structure

## Organized Folders

### `/backend/` - Core Grace Systems
All Grace's Python code and systems

### `/frontend/` - Web UI
React-based web interface

### `/scripts/`
- `/control/` - Grace control interfaces (terminal, monitor, master control)
- `/monitoring/` - Log viewing and monitoring tools
- Other utility scripts

### `/docs/`
- `/system_manifests/` - All documentation and guides (53 files)
- `/quick_guides/` - Quick reference guides

### `/tests/` - All Tests
Integration tests, system tests, validation tests

### `/logs/` - System Logs
- `ingestion.html` - Visual log with clickable links
- `ingestion_visual.log` - Terminal log
- Other log files

### `/storage/` - Knowledge Storage
- `/provenance/` - Source tracking and audit trails
- `/web_knowledge/` - Scraped content
- `/exports/` - Data backups

### `/config/` - Configuration
- `integrated_apis.json` - Approved APIs
- Other config files

### `/databases/` - SQLite Databases
- `grace.db` - Main database
- `metrics.db` - Metrics database

### `/sandbox/` - Sandbox Environments
- `/knowledge_tests/` - Knowledge application testing
- `/api_tests/` - API testing

---

## 🚀 Main Files (Root)

- `README.md` - Main documentation
- `.env` - Environment variables (includes Amp API key)
- `start_grace.ps1` - PowerShell startup
- `START_GRACE.bat` - Batch startup
- `START_GRACE_AND_MONITOR.bat` - Full system startup
- `alembic.ini` - Database migrations

---

## 📖 Documentation (53 Files in `/docs/system_manifests/`)

### Quick Start
- `QUICK_START.md`
- `QUICK_START_CHAT.md`
- `README_START_HERE.md`

### Complete Systems
- `GRACE_COMPLETE_SYSTEMS_MANIFEST.md`
- `ALL_SYSTEMS_CONFIRMED.md`
- `GRACE_IS_RUNNING.md`

### Learning Systems
- `GRACE_WEB_LEARNING_COMPLETE.md`
- `VERIFICATION_AND_ML_COMPLETE.md`
- `AMP_API_INTEGRATION_COMPLETE.md`

### And 44 more detailed guides!

---

## 🎮 Control Scripts (`/scripts/control/`)

- `grace_terminal.bat` - Chat interface
- `grace_control.bat` - Master control panel
- `grace_monitor.bat` - Visual dashboard
- `grace_master_control.py` - Control script
- `grace_terminal_control.py` - Terminal script
- `grace_monitor_dashboard.py` - Dashboard script

---

## 📊 Monitoring Scripts (`/scripts/monitoring/`)

- `view_ingestion_log.bat` - Open visual HTML log
- `view_logs.bat` - View all logs
- `watch_ingestion.bat` - Watch ingestions real-time
- `watch_all_logs.bat` - Watch all logs
- `watch_healing.bat` - Watch self-healing

---

## ✅ Organized and Ready!

**Everything is now in proper folders with clean root directory! 🎉**
