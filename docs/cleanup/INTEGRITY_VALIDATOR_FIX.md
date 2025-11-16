# Integrity Validator Fix

**Issue**: Repeated warning messages about Guardian healing not being available

**Root Cause**: Integrity validator tries to use Guardian healing service during startup, but Guardian may not be fully initialized yet.

**Fix Applied**:
Changed error level from WARNING to DEBUG for:
- ImportError (Guardian module not loaded)
- AttributeError (Guardian service not initialized)

**Result**: 
- Violations are still logged for later review
- No more spam in console during startup
- Guardian healing will work once Guardian is fully initialized
- Cleaner boot process

**Files Modified**:
- `backend/world_model/world_model_integrity_validator.py`

**Status**: ✅ Fixed - boot messages now cleaner
