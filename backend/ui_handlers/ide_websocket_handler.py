"""Transcendence IDE WebSocket Handler - Complete Integration"""

from pathlib import Path
from datetime import datetime

class IDEWebSocketHandler:
    """Complete WebSocket handler for Transcendence IDE"""
    
    def __init__(self):
        self.sandbox_dir = Path("./sandbox")
        self.quarantine_dir = Path("./sandbox/quarantine")
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
    
    async def handle_message(self, user: str, message: dict) -> dict:
        """Dispatch incoming WebSocket message to handler"""
        
        msg_type = message.get("type")
        handlers = {
            "file_open": self.file_open,
            "file_save": self.file_save,
            "file_create": self.file_create,
            "file_delete": self.file_delete,
            "file_rename": self.file_rename,
            "directory_list": self.directory_list,
            "code_execute": self.code_execute,
            "security_scan": self.security_scan,
            "auto_fix": self.auto_fix,
            "auto_quarantine": self.auto_quarantine,
        }
        
        handler = handlers.get(msg_type)
        if not handler:
            return {"type": "error", "message": f"Unknown message type: {msg_type}"}
        
        try:
            result = await handler(user, message)
            return result
        except Exception as e:
            return {"type": "error", "message": str(e), "original_type": msg_type}
    
    async def file_open(self, user: str, message: dict) -> dict:
        """Load file content with verification"""
        from backend.sandbox_manager import sandbox_manager
        
        file_path = message.get("path")
        if not file_path:
            return {"type": "error", "message": "Missing path"}
        
        try:
            content = await sandbox_manager.read_file(user, file_path)
            
            action_id = f"file_open_{user}_{file_path}_{datetime.utcnow().timestamp()}"
            
            return {
                "type": "file_opened",
                "path": file_path,
                "content": content,
                "size": len(content),
                "timestamp": datetime.utcnow().isoformat(),
                "action_id": action_id
            }
        except Exception as e:
            return {"type": "error", "message": str(e)}
    
    async def file_save(self, user: str, message: dict) -> dict:
        """Save file with verification + governance"""
        from backend.sandbox_manager import sandbox_manager
        from backend.governance import governance_engine
        from backend.verification import verify_action
        
        file_path = message.get("path")
        content = message.get("content", "")
        
        if not file_path:
            return {"type": "error", "message": "Missing path"}
        
        decision = await governance_engine.check(
            actor=user,
            action="ide_file_save",
            resource=file_path,
            payload={"size": len(content), "extension": Path(file_path).suffix}
        )
        
        if decision["decision"] == "block":
            return {
                "type": "file_save_blocked",
                "reason": f"Governance blocked: {decision['policy']}",
                "policy": decision["policy"]
            }
        
        if decision["decision"] == "review":
            return {
                "type": "file_save_pending",
                "reason": "Requires governance review",
                "audit_id": decision["audit_id"]
            }
        
        try:
            result = await sandbox_manager.write_file(user, file_path, content)
            
            verification = await verify_action(
                actor=user,
                action_type="ide_file_save",
                resource=file_path,
                input_data={"content": content[:1000]},
                output_data=result,
                context={"governance_audit_id": decision["audit_id"]}
            )
            
            return {
                "type": "file_saved",
                "path": result["path"],
                "size": result["size"],
                "verified": verification["verified"],
                "verification_id": verification["action_id"],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"type": "error", "message": str(e)}
    
    async def file_create(self, user: str, message: dict) -> dict:
        """Create new file with governance"""
        from backend.sandbox_manager import sandbox_manager
        from backend.governance import governance_engine
        from backend.verification import verify_action
        
        file_path = message.get("path")
        content = message.get("content", "")
        
        if not file_path:
            return {"type": "error", "message": "Missing path"}
        
        decision = await governance_engine.check(
            actor=user,
            action="ide_file_create",
            resource=file_path,
            payload={"path": file_path, "size": len(content)}
        )
        
        if decision["decision"] != "allow":
            return {
                "type": "file_create_blocked",
                "reason": f"Policy: {decision['policy']}",
                "decision": decision["decision"]
            }
        
        try:
            result = await sandbox_manager.write_file(user, file_path, content)
            
            verification = await verify_action(
                actor=user,
                action_type="ide_file_create",
                resource=file_path,
                input_data={"path": file_path},
                output_data=result,
                context={"governance_audit_id": decision["audit_id"]}
            )
            
            return {
                "type": "file_created",
                "path": file_path,
                "size": result["size"],
                "verified": verification["verified"],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"type": "error", "message": str(e)}
    
    async def file_delete(self, user: str, message: dict) -> dict:
        """Delete file with governance approval"""
        from backend.governance import governance_engine
        from backend.verification import verify_action
        
        file_path = message.get("path")
        if not file_path:
            return {"type": "error", "message": "Missing path"}
        
        decision = await governance_engine.check(
            actor=user,
            action="ide_file_delete",
            resource=file_path,
            payload={"path": file_path}
        )
        
        if decision["decision"] == "block":
            return {
                "type": "file_delete_blocked",
                "reason": f"Blocked by policy: {decision['policy']}"
            }
        
        if decision["decision"] == "review":
            return {
                "type": "file_delete_pending",
                "reason": "Requires approval",
                "audit_id": decision["audit_id"]
            }
        
        try:
            full_path = self.sandbox_dir / file_path
            if not full_path.exists():
                return {"type": "error", "message": "File not found"}
            
            full_path.unlink()
            
            verification = await verify_action(
                actor=user,
                action_type="ide_file_delete",
                resource=file_path,
                input_data={"path": file_path},
                output_data={"deleted": True},
                context={"governance_audit_id": decision["audit_id"]}
            )
            
            return {
                "type": "file_deleted",
                "path": file_path,
                "verified": verification["verified"],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"type": "error", "message": str(e)}
    
    async def file_rename(self, user: str, message: dict) -> dict:
        """Rename file with verification"""
        from backend.governance import governance_engine
        from backend.verification import verify_action
        
        old_path = message.get("old_path")
        new_path = message.get("new_path")
        
        if not old_path or not new_path:
            return {"type": "error", "message": "Missing old_path or new_path"}
        
        decision = await governance_engine.check(
            actor=user,
            action="ide_file_rename",
            resource=f"{old_path} -> {new_path}",
            payload={"old_path": old_path, "new_path": new_path}
        )
        
        if decision["decision"] != "allow":
            return {
                "type": "file_rename_blocked",
                "reason": f"Policy: {decision['policy']}"
            }
        
        try:
            old_full = self.sandbox_dir / old_path
            new_full = self.sandbox_dir / new_path
            
            if not old_full.exists():
                return {"type": "error", "message": "Source file not found"}
            
            new_full.parent.mkdir(parents=True, exist_ok=True)
            old_full.rename(new_full)
            
            verification = await verify_action(
                actor=user,
                action_type="ide_file_rename",
                resource=new_path,
                input_data={"old_path": old_path, "new_path": new_path},
                output_data={"renamed": True},
                context={"governance_audit_id": decision["audit_id"]}
            )
            
            return {
                "type": "file_renamed",
                "old_path": old_path,
                "new_path": new_path,
                "verified": verification["verified"],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"type": "error", "message": str(e)}
    
    async def directory_list(self, user: str, message: dict) -> dict:
        """Get file tree with metadata"""
        from backend.sandbox_manager import sandbox_manager
        
        try:
            files = await sandbox_manager.list_files(user)
            
            tree = self._build_tree(files)
            
            return {
                "type": "directory_tree",
                "tree": tree,
                "file_count": len(files),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"type": "error", "message": str(e)}
    
    def _build_tree(self, files: list) -> dict:
        """Build hierarchical tree from flat file list"""
        tree = {}
        
        for file in files:
            parts = Path(file["path"]).parts
            current = tree
            
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    current[part] = file
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
        
        return tree
    
    async def code_execute(self, user: str, message: dict) -> dict:
        """Run code in sandbox with multi-language support"""
        from backend.sandbox_manager import sandbox_manager
        from backend.governance import governance_engine
        from backend.hunter import hunter
        from backend.verification import verify_action
        
        language = message.get("language", "python")
        code = message.get("code", "")
        file_path = message.get("file_path")
        
        decision = await governance_engine.check(
            actor=user,
            action="ide_code_execute",
            resource=f"execute_{language}",
            payload={"language": language, "code_length": len(code)}
        )
        
        if decision["decision"] == "block":
            return {
                "type": "execution_blocked",
                "reason": f"Blocked by policy: {decision['policy']}"
            }
        
        alerts = await hunter.inspect(
            user,
            "ide_code_execute",
            language,
            {"code": code[:1000], "language": language}
        )
        
        if alerts:
            return {
                "type": "execution_blocked",
                "reason": f"{len(alerts)} security alerts triggered",
                "alerts": [{"rule": a[0], "event_id": a[1]} for a in alerts]
            }
        
        try:
            if file_path:
                command = self._get_run_command(language, file_path)
            else:
                temp_file = f"temp_{user}_{datetime.utcnow().timestamp()}.{self._get_extension(language)}"
                await sandbox_manager.write_file(user, temp_file, code)
                command = self._get_run_command(language, temp_file)
                file_path = temp_file
            
            stdout, stderr, exit_code, duration_ms = await sandbox_manager.run_command(
                user, command, file_path
            )
            
            verification = await verify_action(
                actor=user,
                action_type="ide_code_execute",
                resource=file_path,
                input_data={"code": code[:500], "language": language},
                output_data={"exit_code": exit_code, "duration_ms": duration_ms},
                context={"governance_audit_id": decision["audit_id"]}
            )
            
            return {
                "type": "execution_result",
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "duration_ms": duration_ms,
                "success": exit_code == 0,
                "verified": verification["verified"],
                "language": language,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"type": "error", "message": str(e)}
    
    def _get_run_command(self, language: str, file_path: str) -> str:
        """Get execution command for language"""
        commands = {
            "python": f"python {file_path}",
            "python3": f"python3 {file_path}",
            "javascript": f"node {file_path}",
            "bash": f"bash {file_path}",
            "sh": f"sh {file_path}",
        }
        return commands.get(language, f"python {file_path}")
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": "py",
            "python3": "py",
            "javascript": "js",
            "bash": "sh",
            "sh": "sh",
        }
        return extensions.get(language, "txt")
    
    async def security_scan(self, user: str, message: dict) -> dict:
        """Hunter integration for security scanning"""
        from backend.hunter import hunter
        from backend.sandbox_manager import sandbox_manager
        
        file_path = message.get("file_path")
        if not file_path:
            return {"type": "error", "message": "Missing file_path"}
        
        try:
            content = await sandbox_manager.read_file(user, file_path)
            
            alerts = await hunter.inspect(
                user,
                "ide_security_scan",
                file_path,
                {"content": content[:5000], "file_path": file_path}
            )
            
            from grace_ide.api.security import security_engine
            scan_result = await security_engine.scan_content(content, file_path)
            
            return {
                "type": "security_scan_result",
                "file": file_path,
                "hunter_alerts": len(alerts),
                "alerts": [{"rule": a[0], "event_id": a[1]} for a in alerts],
                "static_analysis": scan_result,
                "risk_score": scan_result["risk_score"],
                "recommendation": scan_result["recommendation"],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"type": "error", "message": str(e)}
    
    async def auto_fix(self, user: str, message: dict) -> dict:
        """Apply automated fixes to code issues"""
        from backend.sandbox_manager import sandbox_manager
        from backend.verification import verify_action
        
        file_path = message.get("file_path")
        issue = message.get("issue", "")
        
        if not file_path:
            return {"type": "error", "message": "Missing file_path"}
        
        try:
            content = await sandbox_manager.read_file(user, file_path)
            
            fixed_content = await self._apply_auto_fixes(content, issue)
            
            result = await sandbox_manager.write_file(user, file_path, fixed_content)
            
            verification = await verify_action(
                actor=user,
                action_type="ide_auto_fix",
                resource=file_path,
                input_data={"issue": issue, "original_size": len(content)},
                output_data={"fixed_size": len(fixed_content)},
                context={"auto_fix": True}
            )
            
            return {
                "type": "auto_fix_applied",
                "file": file_path,
                "issue": issue,
                "changes_made": True,
                "verified": verification["verified"],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"type": "error", "message": str(e)}
    
    async def _apply_auto_fixes(self, content: str, issue: str) -> str:
        """Apply simple automated fixes"""
        
        if "hardcoded password" in issue.lower():
            import re
            content = re.sub(
                r'password\s*=\s*["\'][^"\']+["\']',
                'password = os.getenv("PASSWORD")',
                content,
                flags=re.IGNORECASE
            )
        
        if "eval" in issue.lower():
            content = content.replace("eval(", "# UNSAFE: eval(")
        
        if "exec" in issue.lower():
            content = content.replace("exec(", "# UNSAFE: exec(")
        
        return content
    
    async def auto_quarantine(self, user: str, message: dict) -> dict:
        """Move dangerous files to quarantine"""
        from backend.sandbox_manager import sandbox_manager
        from backend.governance import governance_engine
        from backend.verification import verify_action
        
        file_path = message.get("file_path")
        if not file_path:
            return {"type": "error", "message": "Missing file_path"}
        
        decision = await governance_engine.check(
            actor=user,
            action="ide_quarantine",
            resource=file_path,
            payload={"file_path": file_path}
        )
        
        if decision["decision"] == "block":
            return {
                "type": "quarantine_blocked",
                "reason": f"Blocked: {decision['policy']}"
            }
        
        try:
            content = await sandbox_manager.read_file(user, file_path)
            
            quarantine_file = f"quarantine/{user}_{datetime.utcnow().timestamp()}_{Path(file_path).name}"
            
            await sandbox_manager.write_file(user, quarantine_file, content)
            
            original_full = self.sandbox_dir / file_path
            if original_full.exists():
                original_full.unlink()
            
            verification = await verify_action(
                actor=user,
                action_type="ide_quarantine",
                resource=file_path,
                input_data={"file_path": file_path},
                output_data={"quarantine_path": quarantine_file},
                context={"governance_audit_id": decision["audit_id"]}
            )
            
            return {
                "type": "file_quarantined",
                "original_path": file_path,
                "quarantine_path": quarantine_file,
                "verified": verification["verified"],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"type": "error", "message": str(e)}

ide_ws_handler = IDEWebSocketHandler()
