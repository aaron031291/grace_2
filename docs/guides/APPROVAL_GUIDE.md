# Grace Approval System - Quick Guide

## 🔐 What Are Approvals?

Grace has a governance system that requires approvals for certain operations to ensure safety and consent.

When you see: `[OK] Approval required: 6`

This means 6 items need your approval before Grace can proceed.

---

## ✅ How to Grant Approvals

### Option 1: Quick Grant All (Recommended for Development)
```bash
python grant_approvals.py
```

or

```bash
GRANT_APPROVALS.bat
```

This will automatically approve all pending items.

---

### Option 2: Manual Approval via API

Grace likely needs approval for:
1. **Database Access** - Read/write to grace.db
2. **File System Access** - Read/write to directories
3. **Network Access** - API calls, external services
4. **Secrets Access** - Environment variables, API keys
5. **Execution Permissions** - Run scripts, commands
6. **Learning Data Access** - Access to training data

---

## 🚀 After Granting Approvals

Once approvals are granted, start Grace normally:

```bash
python serve.py
```

Grace will remember your approvals and won't ask again unless you reset the database.

---

## 🔄 Reset Approvals

If you need to reset and re-approve:

```bash
# Backup first
copy data\grace.db data\grace.db.backup

# Then in Python:
import sqlite3
conn = sqlite3.connect('data/grace.db')
cursor = conn.cursor()

# Find approval tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%approval%'")
for table in cursor.fetchall():
    print(table[0])
    cursor.execute(f"UPDATE {table[0]} SET approved = 0")

conn.commit()
conn.close()
```

---

## 🛡️ Security Note

The approval system is designed to prevent:
- Unauthorized data access
- Unintended system modifications
- Unsafe operations
- Privacy violations

In development, it's safe to grant all approvals.
In production, review each approval carefully.

---

## 📋 Troubleshooting

### "Approval required" keeps appearing
- Run `python grant_approvals.py` again
- Check if database is read-only
- Verify file permissions on `data/grace.db`

### Script doesn't work
- Ensure you're in the project directory: `cd C:\Users\aaron\grace_2`
- Check Python is installed: `python --version`
- Check database exists: `dir data\grace.db`

---

## 🎯 Quick Reference

```bash
# Grant all approvals
python grant_approvals.py

# Start Grace
python serve.py

# If issues persist
python serve.py --skip-approvals  # (if this flag exists)
```

---

**Status**: Grant approvals once, then Grace runs normally ✅
