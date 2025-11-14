"""
Startup Self-Healing
Runs BEFORE Grace boots to fix common startup issues
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

class StartupHealer:
    """Pre-boot self-healing system"""
    
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        self.project_root = Path(__file__).parent.parent
        
    async def run_preflight_healing(self):
        """Run all startup healing checks"""
        print("\n" + "="*60)
        print("GRACE STARTUP SELF-HEALING")
        print("="*60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        checks = [
            ("Database connectivity", self._check_database),
            ("Database schema", self._check_schema),
            ("Port availability", self._check_ports),
            ("File permissions", self._check_permissions),
            ("Environment variables", self._check_env),
            ("Dependencies", self._check_dependencies),
            ("Circular imports", self._check_imports),
            ("Log directory", self._check_logs),
        ]
        
        for check_name, check_func in checks:
            print(f"[CHECK] {check_name}...", end=" ")
            try:
                result = await check_func()
                if result["ok"]:
                    print("[OK]")
                else:
                    print(f"[ISSUE] {result['issue']}")
                    self.issues_found.append(result)
                    
                    if "fix" in result:
                        print(f"  [FIX] Applying fix...")
                        fix_result = await result["fix"]()
                        if fix_result:
                            print(f"  [OK] Fixed!")
                            self.fixes_applied.append(check_name)
                        else:
                            print(f"  [FAIL] Could not auto-fix")
            except Exception as e:
                print(f"[ERROR] {e}")
                self.issues_found.append({"check": check_name, "error": str(e)})
        
        print()
        print("="*60)
        print(f"Issues found: {len(self.issues_found)}")
        print(f"Fixes applied: {len(self.fixes_applied)}")
        print("="*60)
        print()
        
        if len(self.fixes_applied) > 0:
            print("[INFO] Applied fixes. Grace should start cleanly now.")
        
        return len([i for i in self.issues_found if "fix" not in i]) == 0
    
    async def _check_database(self):
        """Check database file exists and is accessible"""
        db_path = self.project_root / "backend" / "grace.db"
        
        if not db_path.exists():
            return {
                "ok": False,
                "issue": "Database file missing",
                "fix": lambda: self._create_database()
            }
        
        # Check if database is locked
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path), timeout=1)
            conn.execute("SELECT 1")
            conn.close()
            return {"ok": True}
        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                return {
                    "ok": False,
                    "issue": "Database is locked",
                    "fix": lambda: self._unlock_database(db_path)
                }
            return {"ok": False, "issue": str(e)}
    
    async def _create_database(self):
        """Initialize database"""
        try:
            os.system("cd backend && python -m alembic upgrade head")
            return True
        except:
            return False
    
    async def _unlock_database(self, db_path):
        """Unlock database by removing lock files"""
        try:
            shm = db_path.parent / f"{db_path.name}-shm"
            wal = db_path.parent / f"{db_path.name}-wal"
            
            if shm.exists():
                shm.unlink()
            if wal.exists():
                wal.unlink()
            
            await asyncio.sleep(0.5)
            return True
        except:
            return False
    
    async def _check_schema(self):
        """Check if database schema is up to date"""
        try:
            # Check if verification_events has passed column
            import sqlite3
            db_path = self.project_root / "backend" / "grace.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("PRAGMA table_info(verification_events)")
            columns = [row[1] for row in cursor.fetchall()]
            conn.close()
            
            if "passed" not in columns:
                return {
                    "ok": False,
                    "issue": "verification_events missing 'passed' column",
                    "fix": lambda: self._run_migrations()
                }
            
            # Check if playbooks has risk_level
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("PRAGMA table_info(playbooks)")
            columns = [row[1] for row in cursor.fetchall()]
            conn.close()
            
            if "risk_level" not in columns or "autonomy_tier" not in columns:
                return {
                    "ok": False,
                    "issue": "playbooks missing risk_level/autonomy_tier",
                    "fix": lambda: self._run_migrations()
                }
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "issue": f"Schema check failed: {e}"}
    
    async def _run_migrations(self):
        """Run Alembic migrations"""
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except:
            return False
    
    async def _check_ports(self):
        """Check if required ports are available"""
        import socket
        
        ports_to_check = [8000]  # Backend port
        
        for port in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                return {
                    "ok": False,
                    "issue": f"Port {port} already in use"
                }
        
        return {"ok": True}
    
    async def _check_permissions(self):
        """Check file system permissions"""
        critical_dirs = [
            self.project_root / "logs",
            self.project_root / "storage",
            self.project_root / "ml_artifacts",
        ]
        
        for directory in critical_dirs:
            if not directory.exists():
                return {
                    "ok": False,
                    "issue": f"Directory missing: {directory.name}",
                    "fix": lambda d=directory: self._create_directory(d)
                }
            
            if not os.access(directory, os.W_OK):
                return {
                    "ok": False,
                    "issue": f"No write permission: {directory.name}"
                }
        
        return {"ok": True}
    
    async def _create_directory(self, path):
        """Create missing directory"""
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except:
            return False
    
    async def _check_env(self):
        """Check critical environment variables"""
        critical_vars = ["SECRET_KEY", "DATABASE_URL"]
        
        for var in critical_vars:
            if not os.getenv(var):
                return {
                    "ok": False,
                    "issue": f"Missing env var: {var}"
                }
        
        return {"ok": True}
    
    async def _check_dependencies(self):
        """Check if critical Python packages are installed"""
        critical_packages = ["fastapi", "sqlalchemy", "uvicorn"]
        
        for package in critical_packages:
            try:
                __import__(package)
            except ImportError:
                return {
                    "ok": False,
                    "issue": f"Missing package: {package}"
                }
        
        return {"ok": True}
    
    async def _check_imports(self):
        """Check for circular import issues"""
        try:
            # Try importing critical modules
            sys.path.insert(0, str(self.project_root))
            
            from backend.avn_avm import VerificationEvent
            from backend.self_heal_models import Playbook
            
            # Check if VerificationEvent has passed attribute
            if not hasattr(VerificationEvent, 'passed'):
                return {
                    "ok": False,
                    "issue": "VerificationEvent missing 'passed' attribute (circular import)"
                }
            
            # Check if Playbook has risk_level
            if not hasattr(Playbook, 'risk_level'):
                return {
                    "ok": False,
                    "issue": "Playbook missing 'risk_level' attribute"
                }
            
            return {"ok": True}
        except ImportError as e:
            return {
                "ok": False,
                "issue": f"Import error: {str(e)}"
            }
    
    async def _check_logs(self):
        """Check log directory exists and is writable"""
        log_dir = self.project_root / "logs"
        
        if not log_dir.exists():
            return {
                "ok": False,
                "issue": "Log directory missing",
                "fix": lambda: self._create_directory(log_dir)
            }
        
        # Try to write a test file
        test_file = log_dir / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
            return {"ok": True}
        except:
            return {
                "ok": False,
                "issue": "Log directory not writable"
            }


async def main():
    """Run startup healing"""
    healer = StartupHealer()
    success = await healer.run_preflight_healing()
    
    if not success:
        print("[WARNING] Some issues could not be fixed automatically.")
        print("[WARNING] Grace may experience startup problems.")
        print()
    
    return success


if __name__ == "__main__":
    asyncio.run(main())
