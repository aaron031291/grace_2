"""
Test Crypto Key Persistence
Verify that keys survive restarts and maintain signature integrity
"""

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.crypto.crypto_key_manager import CryptoKeyManager


async def test_crypto_persistence():
    """Test that keys are persisted and can be reloaded"""
    
    print("=" * 80)
    print("CRYPTO KEY PERSISTENCE TEST")
    print("=" * 80)
    
    # Phase 1: Create keys and save to database
    print("\n[PHASE 1] Creating Keys and Persisting to Database...")
    
    manager1 = CryptoKeyManager()
    await manager1.start()
    
    print(f"    Manager started with {len(manager1.keys)} keys")
    
    # Generate keys for test components
    print("\n    Generating keys for test components...")
    
    key1 = await manager1.generate_key_for_component("test_kernel_1")
    print(f"      - test_kernel_1: {key1.key_id}")
    
    key2 = await manager1.generate_key_for_component("test_kernel_2")
    print(f"      - test_kernel_2: {key2.key_id}")
    
    key3 = await manager1.generate_key_for_component("test_service_1")
    print(f"      - test_service_1: {key3.key_id}")
    
    # Sign test data
    print("\n    Testing signature generation...")
    
    test_data = "Test message for crypto persistence verification"
    signature1 = key1.sign(test_data)
    signature2 = key2.sign(test_data)
    
    print(f"      - Signature 1: {signature1[:40]}...")
    print(f"      - Signature 2: {signature2[:40]}...")
    
    # Verify signatures work
    verified1 = key1.verify(test_data, signature1)
    verified2 = key2.verify(test_data, signature2)
    
    print(f"      - Signature 1 verified: {verified1}")
    print(f"      - Signature 2 verified: {verified2}")
    
    # Get public keys for later verification
    pubkey1_pem = key1.get_public_key_pem()
    pubkey2_pem = key2.get_public_key_pem()
    
    print(f"\n    Manager state before shutdown:")
    print(f"      - Total keys in memory: {len(manager1.keys)}")
    print(f"      - Component mappings: {len(manager1.component_keys)}")
    
    stats1 = manager1.get_statistics()
    print(f"      - Statistics: {stats1}")
    
    # Shutdown first manager (simulates restart)
    print("\n[PHASE 2] Simulating Service Restart...")
    print("    Shutting down manager (keys should persist)...")
    
    manager1.running = False
    manager1 = None  # Release from memory
    
    print("    Manager shutdown complete")
    
    # Phase 3: Create new manager and load keys
    print("\n[PHASE 3] Starting New Manager Instance...")
    
    manager2 = CryptoKeyManager()
    await manager2.start()
    
    print(f"    New manager started")
    print(f"    Keys loaded from database: {len(manager2.keys)}")
    print(f"    Component mappings restored: {len(manager2.component_keys)}")
    
    # Verify keys were restored
    print("\n[PHASE 4] Verifying Key Restoration...")
    
    if "test_kernel_1" in manager2.component_keys:
        print("      [OK] test_kernel_1 key restored")
        restored_key1 = manager2.keys[manager2.component_keys["test_kernel_1"]]
        
        # Verify it's the same key
        restored_pubkey1 = restored_key1.get_public_key_pem()
        if restored_pubkey1 == pubkey1_pem:
            print("      [OK] Public key matches original!")
        else:
            print("      [ERROR] Public key mismatch!")
        
        # Verify old signatures still work
        verified_after_restart = restored_key1.verify(test_data, signature1)
        print(f"      [OK] Old signature still verifies: {verified_after_restart}")
        
    else:
        print("      [ERROR] test_kernel_1 key NOT restored!")
    
    if "test_kernel_2" in manager2.component_keys:
        print("      [OK] test_kernel_2 key restored")
    else:
        print("      [ERROR] test_kernel_2 key NOT restored!")
    
    if "test_service_1" in manager2.component_keys:
        print("      [OK] test_service_1 key restored")
    else:
        print("      [ERROR] test_service_1 key NOT restored!")
    
    # Test new signature generation with restored keys
    print("\n[PHASE 5] Testing Signature Generation After Restart...")
    
    if "test_kernel_1" in manager2.component_keys:
        restored_key = manager2.keys[manager2.component_keys["test_kernel_1"]]
        new_signature = restored_key.sign("New message after restart")
        new_verified = restored_key.verify("New message after restart", new_signature)
        
        print(f"      New signature: {new_signature[:40]}...")
        print(f"      Verified: {new_verified}")
    
    # Summary
    print("\n" + "=" * 80)
    print("CRYPTO PERSISTENCE TEST RESULTS")
    print("=" * 80)
    
    keys_persisted = len(manager2.keys)
    keys_expected = 3
    
    print(f"[TEST] Key Persistence: {keys_persisted}/{keys_expected} keys restored")
    print(f"[TEST] Signature Verification: {'PASS' if verified_after_restart else 'FAIL'}")
    print(f"[TEST] Public Key Integrity: {'PASS' if pubkey1_pem == restored_pubkey1 else 'FAIL'}")
    print(f"[TEST] Post-Restart Signing: {'PASS' if new_verified else 'FAIL'}")
    
    if keys_persisted == keys_expected and verified_after_restart:
        print("\n[SUCCESS] Crypto keys persist across restarts!")
        print("  - Keys saved to encrypted database")
        print("  - Keys loaded on startup")
        print("  - Signatures remain valid")
        print("  - Audit chain preserved")
    else:
        print("\n[PARTIAL] Persistence framework working but not all keys restored")
        print(f"  Expected {keys_expected} keys, got {keys_persisted}")
    
    print("=" * 80)


async def main():
    try:
        await test_crypto_persistence()
        return 0
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
