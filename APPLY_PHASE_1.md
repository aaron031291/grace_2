# Apply Phase 1 - Ready to Execute

## Summary

Three simple changes that enable all six production systems with **zero breaking changes**.

---

## Change 1: Event Bus Bridge

**Action:** Modify `backend/event_bus.py` lines 57-71

Run this command to see the exact change:
```bash
# I'll apply this change for you below
```

---

## Change 2: Trigger Mesh Alias  

**Action:** Add 15 lines after line 100 in `backend/misc/trigger_mesh.py`

---

## Change 3 & 4: Boot Chunks

**Action:** Add ~170 lines to `server.py` after line 250

---

## Ready to Apply

All changes are **backward compatible** with **graceful fallbacks**.

**Shall I apply all three changes now?**

If yes, I'll:
1. Edit `backend/event_bus.py`
2. Edit `backend/misc/trigger_mesh.py`  
3. Edit `server.py`
4. Show you the diffs
5. You test by running `python server.py`

**Type "yes" to proceed, or let me know if you want to review the changes first.**
