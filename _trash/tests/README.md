# Tests Directory

## Structure

### `e2e/` - End-to-End Tests (26 files)
Complete system integration tests:
- `FINAL_COMPLETE_TEST.py` - Quick validation
- `test_layer1_pipeline.py` - Comprehensive Layer 1 test
- `test_multi_os_fabric_e2e.py` - Multi-OS tests
- `test_integrated_orchestration_e2e.py` - Full orchestration
- And more...

### `unit/` - Unit Tests
Component-specific tests

### `integration/` - Integration Tests
Multi-component integration tests

---

Run tests from project root:
```bash
python tests/e2e/FINAL_COMPLETE_TEST.py
python -m tests.e2e.test_layer1_pipeline
```
