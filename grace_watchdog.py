"""
Grace Watchdog - Process Supervisor
External supervisor that keeps Grace running

Features:
- Monitors serve.py process
- Auto-restarts on crash
- Distinguishes kill switch (manual stop) vs crash
- Alerts on restart
- Logs all restart events
"""

import subprocess
import time
import signal
import sys
import os
from pathlib import Path
from datetime import datetime
import json

GRACE_DIR = Path(__file__).parent
STATUS_FILE = GRACE_DIR / "grace_state.json"
LOG_FILE = GRACE_DIR / "watchdog.log"


class GraceWatchdog:
    """External process supervisor for Grace"""
    
    def __init__(self):
        self.process = None
        self.restart_count = 0
        self.start_time = None
        self.manual_shutdown = False
        
        # Load previous state
        self.load_state()
    
    def load_state(self):
        """Load Grace state from file"""
        if STATUS_FILE.exists():
            try:
                with open(STATUS_FILE, 'r') as f:
                    state = json.load(f)
                    self.manual_shutdown = state.get("manual_shutdown", False)
            except:
                pass
    
    def save_state(self, manual=False):
        """Save Grace state to file"""
        try:
            with open(STATUS_FILE, 'w') as f:
                json.dump({
                    "manual_shutdown": manual,
                    "last_update": datetime.utcnow().isoformat(),
                    "restart_count": self.restart_count
                }, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save state: {e}")
    
    def log(self, message: str, level="INFO"):
        """Write to watchdog log"""
        timestamp = datetime.utcnow().isoformat()
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        print(log_line.strip())
        
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except:
            pass
    
    def send_alert(self, event_type: str, details: dict):
        """Send alert about restart event"""
        
        alert = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details,
            "restart_count": self.restart_count
        }
        
        # Log to file
        alert_file = GRACE_DIR / "alerts" / f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        alert_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(alert_file, 'w') as f:
                json.dump(alert, f, indent=2)
            
            self.log(f"ALERT: {event_type} - {details}", "ALERT")
        except Exception as e:
            self.log(f"Failed to send alert: {e}", "ERROR")
    
    def is_grace_running(self) -> bool:
        """Check if Grace process is running"""
        if not self.process:
            return False
        
        return self.process.poll() is None
    
    def start_grace(self):
        """Start Grace backend"""
        
        self.log("Starting Grace backend (serve.py)...")
        self.start_time = datetime.utcnow()
        
        try:
            self.process = subprocess.Popen(
                [sys.executable, "serve.py"],
                cwd=str(GRACE_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.log(f"✅ Grace started (PID: {self.process.pid})")
            self.save_state(manual=False)
            
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to start Grace: {e}", "ERROR")
            self.send_alert("grace.start.failed", {"error": str(e)})
            return False
    
    def stop_grace(self, manual=False):
        """Stop Grace backend"""
        
        if self.process and self.is_grace_running():
            self.log(f"Stopping Grace (manual={manual})...")
            self.manual_shutdown = manual
            self.save_state(manual=manual)
            
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                self.log("✅ Grace stopped gracefully")
            except:
                self.process.kill()
                self.log("⚠️ Grace force killed")
            
            self.process = None
    
    def check_and_restart(self):
        """Check Grace health and restart if needed"""
        
        if not self.is_grace_running():
            # Grace is not running
            
            uptime = 0
            if self.start_time:
                uptime = (datetime.utcnow() - self.start_time).total_seconds()
            
            # Was this a manual shutdown?
            if self.manual_shutdown:
                self.log("ℹ️ Grace stopped manually (kill switch) - not auto-restarting")
                return False
            
            # Was this a crash (died too quickly)?
            if uptime < 30:
                self.log(f"⚠️ Grace crashed after {uptime:.0f}s - possible boot failure", "WARN")
                reason = "crash_detected"
            else:
                self.log(f"⚠️ Grace died unexpectedly after {uptime:.0f}s", "WARN")
                reason = "unexpected_exit"
            
            # Attempt restart
            self.restart_count += 1
            
            self.send_alert("grace.restart.initiated", {
                "reason": reason,
                "uptime_seconds": uptime,
                "restart_attempt": self.restart_count
            })
            
            self.log(f"🔄 Auto-restarting Grace (attempt {self.restart_count})...")
            
            if self.start_grace():
                self.send_alert("grace.restart.success", {
                    "restart_attempt": self.restart_count
                })
                return True
            else:
                self.send_alert("grace.restart.failed", {
                    "restart_attempt": self.restart_count
                })
                return False
        
        return True  # Grace is running fine
    
    def run(self):
        """Main watchdog loop"""
        
        self.log("="*70)
        self.log("GRACE WATCHDOG - Process Supervisor Starting")
        self.log("="*70)
        self.log(f"Working directory: {GRACE_DIR}")
        self.log(f"Status file: {STATUS_FILE}")
        self.log(f"Log file: {LOG_FILE}")
        self.log("="*70)
        
        # Check if Grace is already running
        if not self.is_grace_running():
            self.log("Grace not running, starting...")
            self.start_grace()
        else:
            self.log(f"Grace already running (PID: {self.process.pid})")
        
        # Monitor loop
        try:
            while True:
                time.sleep(5)  # Check every 5 seconds
                
                if not self.check_and_restart():
                    # Too many failures, pause for a bit
                    if self.restart_count >= 5:
                        self.log("🚨 Too many restart attempts, pausing for 60s", "ERROR")
                        self.send_alert("grace.restart.excessive", {
                            "restart_count": self.restart_count,
                            "action": "paused_supervision"
                        })
                        time.sleep(60)
                        self.restart_count = 0  # Reset counter
        
        except KeyboardInterrupt:
            self.log("\n👋 Watchdog shutting down (Ctrl+C)")
            self.stop_grace(manual=True)
            self.log("Watchdog stopped")
        
        except Exception as e:
            self.log(f"🚨 Watchdog error: {e}", "CRITICAL")
            self.send_alert("watchdog.error", {"error": str(e)})


def main():
    """Run the watchdog"""
    watchdog = GraceWatchdog()
    watchdog.run()


if __name__ == "__main__":
    main()
