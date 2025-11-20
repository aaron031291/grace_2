"""
Production Readiness Audit for Grace AI System
Comprehensive check of all subsystems, tables, kernels, and crypto logging
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect, text
from backend.models import engine, Base
from backend.immutable_log import immutable_log


class ProductionReadinessAuditor:
    """Comprehensive production readiness checker"""
    
    def __init__(self):
        self.results = {
            'database': {},
            'subsystems': {},
            'kernels': {},
            'crypto': {},
            'config': {},
            'errors': []
        }
    
    async def run_full_audit(self) -> Dict[str, Any]:
        """Run complete production readiness audit"""
        
        print("="*80)
        print("GRACE PRODUCTION READINESS AUDIT")
        print("="*80)
        print()
        
        # 1. Database Schema Check
        await self.audit_database_schema()
        
        # 2. Subsystems Check
        await self.audit_subsystems()
        
        # 3. Kernel System Check
        await self.audit_kernels()
        
        # 4. Cryptographic Logging Check
        await self.audit_crypto_logging()
        
        # 5. Configuration Check
        await self.audit_configuration()
        
        # 6. Generate Report
        self.generate_report()
        
        return self.results
    
    async def audit_database_schema(self):
        """Verify all tables exist and are properly configured"""
        print("[1/5] DATABASE SCHEMA AUDIT")
        print("-" * 80)

        async with engine.begin() as conn:
            # Get all tables using async query
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ))
            existing_tables = [row[0] for row in result.fetchall()]
            
            # Get expected tables from models
            expected_tables = [table.name for table in Base.metadata.sorted_tables]
            
            missing_tables = set(expected_tables) - set(existing_tables)
            extra_tables = set(existing_tables) - set(expected_tables)
            
            self.results['database'] = {
                'total_tables': len(existing_tables),
                'expected_tables': len(expected_tables),
                'missing_tables': list(missing_tables),
                'extra_tables': list(extra_tables),
                'status': 'OK' if not missing_tables else 'MISSING_TABLES'
            }
            
            print(f"  Total tables: {len(existing_tables)}")
            print(f"  Expected tables: {len(expected_tables)}")
            
            if missing_tables:
                print(f"  [WARN] Missing tables: {', '.join(missing_tables)}")
                self.results['errors'].append(f"Missing tables: {missing_tables}")
            else:
                print("  [OK] All expected tables exist")

            if extra_tables:
                print(f"  [INFO] Extra tables: {', '.join(extra_tables)}")

            # Check critical tables
            critical_tables = [
                'users', 'messages', 'immutable_log', 'verification_events',
                'governance_policies', 'hunter_rules', 'code_patterns',
                'memory_artifacts', 'constitutional_principles'
            ]

            missing_critical = [t for t in critical_tables if t not in existing_tables]
            if missing_critical:
                print(f"  [FAIL] CRITICAL: Missing critical tables: {missing_critical}")
                self.results['errors'].append(f"Missing critical tables: {missing_critical}")
            else:
                print("  [OK] All critical tables present")
        
        print()
    
    async def audit_subsystems(self):
        """Check that all subsystems are importable and functional"""
        print("[2/5] SUBSYSTEMS AUDIT")
        print("-" * 80)
        
        subsystems = {
            'trigger_mesh': 'backend.trigger_mesh',
            'immutable_log': 'backend.immutable_log',
            'governance': 'backend.governance',
            'hunter': 'backend.hunter',
            'verification': 'backend.verification',
            'meta_loop': 'backend.meta_loop',
            'self_healing': 'backend.self_healing',
            'parliament': 'backend.parliament_engine',
            'agentic_spine': 'backend.agentic_spine',
            'proactive_intelligence': 'backend.proactive_intelligence',
            'crypto_engine': 'backend.crypto_assignment_engine',
            'memory': 'backend.memory',
            'code_memory': 'backend.code_memory',
            'learning': 'backend.learning_integration',
        }
        
        working = []
        broken = []
        
        for name, module_path in subsystems.items():
            try:
                __import__(module_path)
                working.append(name)
                print(f"  [OK] {name}")
            except Exception as e:
                broken.append((name, str(e)))
                print(f"  [FAIL] {name}: {e}")
                self.results['errors'].append(f"Subsystem {name} failed: {e}")
        
        self.results['subsystems'] = {
            'total': len(subsystems),
            'working': len(working),
            'broken': len(broken),
            'broken_list': [b[0] for b in broken],
            'status': 'OK' if not broken else 'FAILURES'
        }
        
        print(f"\n  Summary: {len(working)}/{len(subsystems)} subsystems operational")
        print()
    
    async def audit_kernels(self):
        """Verify all 9 domain kernels are registered"""
        print("[3/5] KERNEL SYSTEM AUDIT")
        print("-" * 80)
        
        try:
            from backend.kernels import (
                memory_kernel, core_kernel, code_kernel,
                governance_kernel, verification_kernel,
                intelligence_kernel, infrastructure_kernel,
                federation_kernel
            )
            
            kernels = {
                'memory': memory_kernel,
                'core': core_kernel,
                'code': code_kernel,
                'governance': governance_kernel,
                'verification': verification_kernel,
                'intelligence': intelligence_kernel,
                'infrastructure': infrastructure_kernel,
                'federation': federation_kernel,
            }
            
            working_kernels = []
            for name, kernel in kernels.items():
                if kernel and hasattr(kernel, 'domain_name'):
                    working_kernels.append(name)
                    print(f"  [OK] {name}_kernel")
                else:
                    print(f"  [FAIL] {name}_kernel (not initialized)")
            
            self.results['kernels'] = {
                'total': len(kernels),
                'working': len(working_kernels),
                'status': 'OK' if len(working_kernels) == len(kernels) else 'INCOMPLETE'
            }
            
            print(f"\n  Summary: {len(working_kernels)}/{len(kernels)} kernels operational")
            
        except Exception as e:
            print(f"  ❌ Kernel system error: {e}")
            self.results['errors'].append(f"Kernel system: {e}")
            self.results['kernels'] = {'status': 'ERROR', 'error': str(e)}
        
        print()
    
    async def audit_crypto_logging(self):
        """Verify cryptographic operations are logged"""
        print("[4/5] CRYPTOGRAPHIC AUDIT TRAIL")
        print("-" * 80)
        
        try:
            # Test immutable log
            test_entry = await immutable_log.append(
                actor="production_audit",
                action="crypto_audit_test",
                resource="audit_system",
                subsystem="production_readiness",
                payload={"test": True, "timestamp": datetime.utcnow().isoformat()},
                result="test_entry"
            )
            
            print(f"  [OK] Immutable log operational (entry: {test_entry})")

            # Check crypto engine
            from backend.crypto_assignment_engine import crypto_engine

            test_sig = crypto_engine.sign("test_data")
            verified = crypto_engine.verify("test_data", test_sig)

            if verified:
                print("  [OK] Crypto engine operational (Ed25519 signatures)")
            else:
                print("  [FAIL] Crypto verification failed")
                self.results['errors'].append("Crypto verification failed")
            
            self.results['crypto'] = {
                'immutable_log': 'OK',
                'crypto_engine': 'OK' if verified else 'FAILED',
                'status': 'OK' if verified else 'FAILED'
            }
            
        except Exception as e:
            print(f"  [FAIL] Crypto system error: {e}")
            self.results['errors'].append(f"Crypto system: {e}")
            self.results['crypto'] = {'status': 'ERROR', 'error': str(e)}

        print()

    async def audit_configuration(self):
        """Check configuration files"""
        print("[5/5] CONFIGURATION AUDIT")
        print("-" * 80)

        config_files = [
            'config/agentic_config.yaml',
            'config/guardrails.yaml',
            'config/grace_constitution.yaml',
            '.env.example',
        ]

        existing = []
        missing = []

        for config_file in config_files:
            path = Path(config_file)
            if path.exists():
                existing.append(config_file)
                print(f"  [OK] {config_file}")
            else:
                missing.append(config_file)
                print(f"  [WARN] {config_file} (missing)")

        # Check .env
        env_path = Path('.env')
        if env_path.exists():
            print("  [OK] .env (configured)")
        else:
            print("  [WARN] .env (not configured - using defaults)")
        
        self.results['config'] = {
            'total': len(config_files),
            'existing': len(existing),
            'missing': missing,
            'env_configured': env_path.exists(),
            'status': 'OK' if not missing else 'INCOMPLETE'
        }
        
        print()
    
    def generate_report(self):
        """Generate final report"""
        print("="*80)
        print("AUDIT SUMMARY")
        print("="*80)
        print()
        
        # Overall status
        has_errors = len(self.results['errors']) > 0
        has_warnings = (
            self.results['database'].get('status') != 'OK' or
            self.results['subsystems'].get('status') != 'OK' or
            self.results['kernels'].get('status') != 'OK' or
            self.results['crypto'].get('status') != 'OK' or
            self.results['config'].get('status') != 'OK'
        )
        
        if not has_errors and not has_warnings:
            print("[SUCCESS] PRODUCTION READY - All systems operational")
        elif has_errors:
            print("[FAIL] NOT PRODUCTION READY - Critical errors found")
        else:
            print("[WARN] PRODUCTION READY WITH WARNINGS")
        
        print()
        print(f"Database: {self.results['database'].get('status', 'UNKNOWN')}")
        print(f"Subsystems: {self.results['subsystems'].get('status', 'UNKNOWN')}")
        print(f"Kernels: {self.results['kernels'].get('status', 'UNKNOWN')}")
        print(f"Crypto: {self.results['crypto'].get('status', 'UNKNOWN')}")
        print(f"Config: {self.results['config'].get('status', 'UNKNOWN')}")
        
        if self.results['errors']:
            print()
            print("ERRORS:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        print()
        print("="*80)


async def main():
    """Run production readiness audit"""
    auditor = ProductionReadinessAuditor()
    results = await auditor.run_full_audit()
    
    # Return exit code
    return 0 if not results['errors'] else 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

