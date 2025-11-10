import json
import re
from typing import Optional, Dict
from .issue_models import IssueReport
from .models import async_session
from datetime import datetime

class RemedyInference:
    """Analyzes errors and suggests fixes"""
    
    def analyze_error(self, error_text: str, context: dict) -> dict:
        """Parse error and generate fix suggestion"""
        
        if "NameError" in error_text:
            match = re.search(r"name '(\w+)' is not defined", error_text)
            if match:
                var_name = match.group(1)
                return {
                    "explanation": f"Variable '{var_name}' was referenced before being defined.",
                    "likely_cause": "Missing variable declaration or import statement",
                    "suggested_fix": f"Add: {var_name} = None  # or import {var_name}",
                    "action_label": f"Insert stub for '{var_name}'",
                    "action_payload": json.dumps({
                        "type": "insert_line",
                        "content": f"{var_name} = None  # Auto-generated stub",
                        "position": "top"
                    })
                }
        
        elif "ModuleNotFoundError" in error_text:
            match = re.search(r"No module named '(\w+)'", error_text)
            if match:
                module = match.group(1)
                return {
                    "explanation": f"Python module '{module}' is not installed.",
                    "likely_cause": "Missing dependency in environment",
                    "suggested_fix": f"Run: pip install {module}",
                    "action_label": f"Install '{module}'",
                    "action_payload": json.dumps({
                        "type": "pip_install",
                        "package": module
                    })
                }
        
        elif "SyntaxError" in error_text:
            return {
                "explanation": "Code has syntax errors preventing execution.",
                "likely_cause": "Invalid Python syntax (missing colon, parenthesis, etc.)",
                "suggested_fix": "Review the line indicated in the error and fix syntax",
                "action_label": "Show syntax help",
                "action_payload": json.dumps({"type": "show_docs", "topic": "syntax"})
            }
        
        elif "IndentationError" in error_text:
            return {
                "explanation": "Code indentation is incorrect.",
                "likely_cause": "Mixed tabs/spaces or incorrect indent level",
                "suggested_fix": "Ensure consistent 4-space indentation",
                "action_label": "Auto-format code",
                "action_payload": json.dumps({"type": "format_code"})
            }
        
        elif "FileNotFoundError" in error_text:
            match = re.search(r"No such file or directory: '([^']+)'", error_text)
            if match:
                filename = match.group(1)
                return {
                    "explanation": f"File '{filename}' does not exist in the sandbox.",
                    "likely_cause": "Missing file or incorrect path",
                    "suggested_fix": f"Create the file or check the path",
                    "action_label": f"Create '{filename}'",
                    "action_payload": json.dumps({
                        "type": "create_file",
                        "filename": filename,
                        "content": "# Auto-created file\n"
                    })
                }
        
        return {
            "explanation": "An error occurred during execution.",
            "likely_cause": "Check the error details for specifics",
            "suggested_fix": "Review the error message and fix manually",
            "action_label": "View error details",
            "action_payload": json.dumps({"type": "show_error"})
        }
    
    async def log_issue(
        self,
        user: str,
        source: str,
        summary: str,
        details: str,
        context: dict = None
    ) -> int:
        """Log an issue and generate remediation suggestion"""
        
        analysis = self.analyze_error(details, context or {})
        
        async with async_session() as session:
            issue = IssueReport(
                user=user,
                source=source,
                summary=summary,
                details=details,
                explanation=analysis["explanation"],
                likely_cause=analysis["likely_cause"],
                suggested_fix=analysis["suggested_fix"],
                action_label=analysis["action_label"],
                action_payload=analysis["action_payload"],
                status="pending"
            )
            session.add(issue)
            await session.commit()
            await session.refresh(issue)
            
            print(f"✓ Issue logged: {summary[:50]}... (ID: {issue.id})")
            return issue.id
    
    async def apply_fix(self, issue_id: int) -> dict:
        """Apply the suggested fix for an issue"""
        async with async_session() as session:
            issue = await session.get(IssueReport, issue_id)
            if not issue:
                return {"status": "error", "message": "Issue not found"}
            
            if issue.status != "pending":
                return {"status": "error", "message": "Issue already processed"}
            
            try:
                action = json.loads(issue.action_payload)
                
                if action["type"] == "insert_line":
                    result = f"Would insert: {action['content']}"
                    success = True
                
                elif action["type"] == "pip_install":
                    result = f"Would install: {action['package']}"
                    success = True
                
                elif action["type"] == "create_file":
                    result = f"Would create: {action['filename']}"
                    success = True
                
                else:
                    result = "Fix type not implemented yet"
                    success = False
                
                issue.status = "resolved" if success else "failed"
                issue.applied_fix = result
                issue.fix_result = "success" if success else "failed"
                issue.resolved_at = datetime.utcnow()
                await session.commit()
                
                print(f"✓ Applied fix for issue {issue_id}: {result}")
                
                return {
                    "status": "success" if success else "failed",
                    "result": result,
                    "issue_id": issue_id
                }
                
            except Exception as e:
                issue.status = "failed"
                issue.fix_result = str(e)
                await session.commit()
                return {"status": "error", "message": str(e)}

remedy_inference = RemedyInference()
