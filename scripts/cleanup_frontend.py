
import os
import shutil
import fnmatch
from pathlib import Path

# Configuration
FRONTEND_DIR = Path("c:/Users/aaron/grace_2/frontend/src")
LEGACY_DIR = FRONTEND_DIR / "legacy"

# Patterns to KEEP in the main src directory
# These are relative to frontend/src/
KEEP_PATTERNS = [
    "main.tsx",
    "AppChat.tsx",
    "AppChat.css",
    "index.css",
    "config.ts",
    "vite-env.d.ts",
    "api/**/*",
    "types/**/*",
    "components/ChatPanel.tsx",
    "components/ChatPanel.css",
    "components/BackgroundTasksDrawer*.tsx",
    "components/BackgroundTasksDrawer*.css",
    "components/TelemetryStrip.tsx",
    "components/TelemetryStrip.css",
    "components/HistorySearch.tsx",
    "components/HistorySearch.css",
    "components/UserPresence*.tsx",
    "components/UserPresence*.css",
    "components/HealthMeter.tsx",
    "components/HealthMeter.css",
    "components/RemoteCockpit*.tsx",
    "components/RemoteCockpit*.css",
    "components/FileExplorer.tsx",
    "components/FileExplorer.css",
    "hooks/useNotifications.ts",
    "legacy/**/*"  # Don't move legacy itself
]

def should_keep(file_path):
    rel_path = file_path.relative_to(FRONTEND_DIR)
    rel_path_str = str(rel_path).replace("\\", "/")
    
    for pattern in KEEP_PATTERNS:
        if fnmatch.fnmatch(rel_path_str, pattern):
            return True
    
    return False

def main():
    print(f"Cleaning up {FRONTEND_DIR}...")
    
    if not LEGACY_DIR.exists():
        LEGACY_DIR.mkdir(parents=True)
        print(f"Created {LEGACY_DIR}")
    
    moved_count = 0
    
    # Walk through all files in src
    for root, dirs, files in os.walk(FRONTEND_DIR):
        root_path = Path(root)
        
        # Skip legacy directory itself
        if LEGACY_DIR in root_path.parents or root_path == LEGACY_DIR:
            continue
            
        for file in files:
            file_path = root_path / file
            
            if not should_keep(file_path):
                # Determine destination path
                rel_path = file_path.relative_to(FRONTEND_DIR)
                dest_path = LEGACY_DIR / rel_path
                
                # Create parent directories
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                try:
                    shutil.move(str(file_path), str(dest_path))
                    print(f"Moved: {rel_path} -> legacy/{rel_path}")
                    moved_count += 1
                except Exception as e:
                    print(f"Error moving {rel_path}: {e}")
                    
    print(f"\nCleanup complete. Moved {moved_count} files to src/legacy.")

if __name__ == "__main__":
    main()
