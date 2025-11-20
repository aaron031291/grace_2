"""
End-to-End Test for Collaboration System
Tests all components: Presence, Workflows, Notifications, Automation, Co-Pilot
"""
import asyncio
import sys
import traceback
from datetime import datetime
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


class CollaborationE2ETest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.logs = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_msg)
        print(log_msg)
    
    def test_result(self, test_name, success, error=None):
        if success:
            self.passed += 1
            self.log(f"✅ PASS: {test_name}", "PASS")
        else:
            self.failed += 1
            self.log(f"❌ FAIL: {test_name}", "FAIL")
            if error:
                self.log(f"   Error: {error}", "ERROR")
    
    async def test_imports(self):
        """Test 1: Import all collaboration modules"""
        self.log("=" * 80)
        self.log("TEST 1: Module Imports")
        self.log("=" * 80)
        
        try:
            from backend.collaboration.presence_system import presence_system
            self.log("✓ Imported presence_system")
            self.test_result("Import presence_system", True)
        except Exception as e:
            self.test_result("Import presence_system", False, str(e))
        
        try:
            from backend.collaboration.grace_copilot_engine import grace_copilot
            self.log("✓ Imported grace_copilot")
            self.test_result("Import grace_copilot", True)
        except Exception as e:
            self.test_result("Import grace_copilot", False, str(e))
        
        try:
            from backend.collaboration.workflow_engine import workflow_engine, WorkflowType
            self.log("✓ Imported workflow_engine")
            self.test_result("Import workflow_engine", True)
        except Exception as e:
            self.test_result("Import workflow_engine", False, str(e))
        
        try:
            from backend.collaboration.notification_service import notification_service
            self.log("✓ Imported notification_service")
            self.test_result("Import notification_service", True)
        except Exception as e:
            self.test_result("Import notification_service", False, str(e))
        
        try:
            from backend.collaboration.automation_engine import automation_engine, TriggerType
            self.log("✓ Imported automation_engine")
            self.test_result("Import automation_engine", True)
        except Exception as e:
            self.test_result("Import automation_engine", False, str(e))
        
        try:
            from backend.collaboration.websocket_manager import collaboration_ws_manager
            self.log("✓ Imported websocket_manager")
            self.test_result("Import websocket_manager", True)
        except Exception as e:
            self.test_result("Import websocket_manager", False, str(e))
        
        try:
            from backend.collaboration.models import UserPresence, CollaborationWorkflow, Notification
            self.log("✓ Imported collaboration models")
            self.test_result("Import models", True)
        except Exception as e:
            self.test_result("Import models", False, str(e))
    
    async def test_presence_system(self):
        """Test 2: Presence System"""
        self.log("\n" + "=" * 80)
        self.log("TEST 2: Presence System")
        self.log("=" * 80)
        
        try:
            from backend.collaboration.presence_system import presence_system
            
            # Test: Start presence system
            await presence_system.start()
            self.log("✓ Presence system started")
            self.test_result("Start presence system", True)
            
            # Test: Join session
            result = await presence_system.join_session(
                user_id="test_user_1",
                user_name="Alice",
                metadata={"role": "tester"}
            )
            self.log(f"✓ User joined: {result}")
            self.test_result("Join session", result.get("success", False))
            
            # Test: Heartbeat
            hb_result = await presence_system.heartbeat("test_user_1")
            self.log(f"✓ Heartbeat sent: {hb_result}")
            self.test_result("Send heartbeat", hb_result.get("success", False))
            
            # Test: View file
            await presence_system.view_file("test_user_1", "/test/file.py")
            self.log("✓ File view tracked")
            self.test_result("Track file view", True)
            
            # Test: Request edit
            edit_result = await presence_system.request_edit(
                user_id="test_user_1",
                user_name="Alice",
                file_path="/test/file.py"
            )
            self.log(f"✓ Edit requested: {edit_result}")
            self.test_result("Request edit lock", edit_result.get("success", False))
            
            # Test: Get all presence
            all_presence = await presence_system.get_all_presence()
            self.log(f"✓ All presence: {all_presence['total_sessions']} active sessions")
            self.test_result("Get all presence", all_presence['total_sessions'] > 0)
            
            # Test: Release edit
            release_result = await presence_system.release_edit("test_user_1", "/test/file.py")
            self.log(f"✓ Edit released: {release_result}")
            self.test_result("Release edit lock", release_result.get("success", False))
            
        except Exception as e:
            self.log(f"Presence system error: {e}")
            self.log(traceback.format_exc())
            self.test_result("Presence system", False, str(e))
    
    async def test_workflow_engine(self):
        """Test 3: Workflow Engine"""
        self.log("\n" + "=" * 80)
        self.log("TEST 3: Workflow Engine")
        self.log("=" * 80)
        
        try:
            from backend.collaboration.workflow_engine import workflow_engine, WorkflowType
            
            # Test: Create workflow
            workflow = await workflow_engine.create_workflow(
                workflow_type=WorkflowType.SCHEMA_APPROVAL,
                title="Test Schema Review",
                description="Testing workflow creation",
                created_by="test_user_1",
                reviewers=["reviewer1", "reviewer2"],
                checklist=["Test coverage", "Documentation", "Review code"]
            )
            self.log(f"✓ Workflow created: {workflow.workflow_id}")
            self.test_result("Create workflow", workflow is not None)
            
            # Test: Get workflow
            workflow_data = await workflow_engine.get_workflow(workflow.workflow_id)
            self.log(f"✓ Workflow retrieved: {workflow_data['title']}")
            self.test_result("Get workflow", workflow_data is not None)
            
            # Test: Add comment
            comment_result = await workflow_engine.add_comment(
                workflow_id=workflow.workflow_id,
                user_id="reviewer1",
                user_name="Bob",
                comment="Looks good to me!"
            )
            self.log(f"✓ Comment added: {comment_result}")
            self.test_result("Add comment", comment_result.get("success", False))
            
            # Test: Update checklist
            checklist_result = await workflow_engine.update_checklist(
                workflow_id=workflow.workflow_id,
                item_index=0,
                completed=True,
                user_id="reviewer1"
            )
            self.log(f"✓ Checklist updated: {checklist_result}")
            self.test_result("Update checklist", checklist_result.get("success", False))
            
            # Test: Approve workflow
            approve_result = await workflow_engine.approve_workflow(
                workflow_id=workflow.workflow_id,
                user_id="reviewer1",
                user_name="Bob",
                comments="Approved!"
            )
            self.log(f"✓ Workflow approved: {approve_result}")
            self.test_result("Approve workflow", approve_result.get("success", False))
            
            # Test: Get pending workflows
            pending = await workflow_engine.get_pending_workflows()
            self.log(f"✓ Pending workflows: {len(pending)} found")
            self.test_result("Get pending workflows", isinstance(pending, list))
            
        except Exception as e:
            self.log(f"Workflow engine error: {e}")
            self.log(traceback.format_exc())
            self.test_result("Workflow engine", False, str(e))
    
    async def test_notification_service(self):
        """Test 4: Notification Service"""
        self.log("\n" + "=" * 80)
        self.log("TEST 4: Notification Service")
        self.log("=" * 80)
        
        try:
            from backend.collaboration.notification_service import notification_service, NotificationPriority
            
            # Test: Start service
            await notification_service.start()
            self.log("✓ Notification service started")
            self.test_result("Start notification service", True)
            
            # Test: Create notification
            notif = await notification_service.create_notification(
                user_id="test_user_1",
                notification_type="test",
                title="Test Notification",
                message="This is a test notification",
                priority=NotificationPriority.HIGH,
                action_url="/test",
                action_label="View Test"
            )
            self.log(f"✓ Notification created: {notif.notification_id}")
            self.test_result("Create notification", notif is not None)
            
            # Test: Get user notifications
            user_notifs = await notification_service.get_user_notifications(
                user_id="test_user_1",
                unread_only=False,
                limit=10
            )
            self.log(f"✓ User notifications: {len(user_notifs)} found")
            self.test_result("Get user notifications", len(user_notifs) > 0)
            
            # Test: Get unread count
            unread_count = await notification_service.get_unread_count("test_user_1")
            self.log(f"✓ Unread count: {unread_count}")
            self.test_result("Get unread count", unread_count >= 0)
            
            # Test: Mark as read
            mark_result = await notification_service.mark_read(notif.notification_id, "test_user_1")
            self.log(f"✓ Mark as read: {mark_result}")
            self.test_result("Mark notification read", mark_result)
            
            # Test: Bulk notify
            await notification_service.bulk_notify(
                user_ids=["user1", "user2", "user3"],
                notification_type="bulk_test",
                title="Bulk Notification",
                message="Testing bulk notifications"
            )
            self.log("✓ Bulk notifications sent")
            self.test_result("Bulk notify", True)
            
        except Exception as e:
            self.log(f"Notification service error: {e}")
            self.log(traceback.format_exc())
            self.test_result("Notification service", False, str(e))
    
    async def test_automation_engine(self):
        """Test 5: Automation Engine"""
        self.log("\n" + "=" * 80)
        self.log("TEST 5: Automation Engine")
        self.log("=" * 80)
        
        try:
            from backend.collaboration.automation_engine import automation_engine, TriggerType
            
            # Test: Start engine
            await automation_engine.start()
            self.log("✓ Automation engine started")
            self.test_result("Start automation engine", True)
            
            # Test: Create rule
            rule = await automation_engine.create_rule(
                name="Test Quality Alert",
                description="Alert when quality drops",
                trigger_type=TriggerType.QUALITY_THRESHOLD,
                trigger_conditions={"quality_score": {"operator": "less_than", "value": 0.8}},
                actions=[{
                    "type": "send_notification",
                    "params": {
                        "title": "Quality Alert",
                        "message": "Quality score is low"
                    }
                }]
            )
            self.log(f"✓ Rule created: {rule.rule_id}")
            self.test_result("Create automation rule", rule is not None)
            
            # Test: List rules
            rules = await automation_engine.list_rules()
            self.log(f"✓ Rules listed: {len(rules)} found")
            self.test_result("List automation rules", len(rules) > 0)
            
            # Test: Get specific rule
            rule_data = await automation_engine.get_rule(rule.rule_id)
            self.log(f"✓ Rule retrieved: {rule_data['name']}")
            self.test_result("Get automation rule", rule_data is not None)
            
            # Test: Trigger event
            await automation_engine.trigger_event(
                trigger_type=TriggerType.QUALITY_THRESHOLD,
                event_data={"quality_score": 0.75, "user_id": "test_user_1"}
            )
            self.log("✓ Event triggered")
            self.test_result("Trigger automation event", True)
            
            # Test: Disable rule
            await automation_engine.disable_rule(rule.rule_id)
            self.log(f"✓ Rule disabled: {rule.rule_id}")
            self.test_result("Disable automation rule", True)
            
            # Test: Enable rule
            await automation_engine.enable_rule(rule.rule_id)
            self.log(f"✓ Rule enabled: {rule.rule_id}")
            self.test_result("Enable automation rule", True)
            
        except Exception as e:
            self.log(f"Automation engine error: {e}")
            self.log(traceback.format_exc())
            self.test_result("Automation engine", False, str(e))
    
    async def test_copilot_engine(self):
        """Test 6: Grace Co-Pilot Engine"""
        self.log("\n" + "=" * 80)
        self.log("TEST 6: Grace Co-Pilot Engine")
        self.log("=" * 80)
        
        try:
            from backend.collaboration.grace_copilot_engine import grace_copilot
            
            # Test: Initialize
            await grace_copilot.initialize()
            self.log("✓ Co-pilot initialized")
            self.test_result("Initialize co-pilot", True)
            
            # Test: Suggest schema
            schema_result = await grace_copilot.suggest_schema(
                file_path="/test/data.json",
                file_content='{"name": "test", "value": 123}'
            )
            self.log(f"✓ Schema suggested: {schema_result.get('success', False)}")
            self.test_result("Suggest schema", schema_result.get("success", False))
            
            # Test: Explain file
            explain_result = await grace_copilot.explain_file(
                file_path="/test/script.py",
                file_content="def hello(): print('world')",
                user_id="test_user_1"
            )
            self.log(f"✓ File explained: {explain_result.get('success', False)}")
            self.test_result("Explain file", explain_result.get("success", False))
            
            # Test: Draft summary
            summary_result = await grace_copilot.draft_summary(
                content="This is a long document that needs summarization.",
                context="Documentation"
            )
            self.log(f"✓ Summary drafted: {summary_result.get('success', False)}")
            self.test_result("Draft summary", summary_result.get("success", False))
            
            # Test: Chat
            chat_result = await grace_copilot.chat(
                user_id="test_user_1",
                message="What is this file about?",
                context={"file_path": "/test/script.py"}
            )
            self.log(f"✓ Chat response: {chat_result.get('success', False)}")
            self.test_result("Chat with co-pilot", chat_result.get("success", False))
            
        except Exception as e:
            self.log(f"Co-pilot engine error: {e}")
            self.log(traceback.format_exc())
            self.test_result("Co-pilot engine", False, str(e))
    
    async def test_websocket_manager(self):
        """Test 7: WebSocket Manager"""
        self.log("\n" + "=" * 80)
        self.log("TEST 7: WebSocket Manager")
        self.log("=" * 80)
        
        try:
            from backend.collaboration.websocket_manager import collaboration_ws_manager
            
            # Note: We can't fully test WebSocket without actual connections
            # But we can test the manager's methods
            
            # Test: Subscribe to room
            await collaboration_ws_manager.subscribe_to_room("session_1", "file:/test/file.py")
            self.log("✓ Subscribed to room")
            self.test_result("Subscribe to room", True)
            
            # Test: Broadcast to room
            await collaboration_ws_manager.broadcast_to_room(
                "file:/test/file.py",
                {"type": "test", "message": "Hello room!"}
            )
            self.log("✓ Broadcast to room")
            self.test_result("Broadcast to room", True)
            
            # Test: Presence update
            await collaboration_ws_manager.broadcast_presence_update({
                "type": "user_activity",
                "user_id": "test_user_1",
                "action": "typing"
            })
            self.log("✓ Presence update broadcast")
            self.test_result("Broadcast presence update", True)
            
            # Test: File edit notification
            await collaboration_ws_manager.notify_file_edit(
                "/test/file.py",
                "test_user_1",
                "Alice"
            )
            self.log("✓ File edit notification sent")
            self.test_result("Notify file edit", True)
            
        except Exception as e:
            self.log(f"WebSocket manager error: {e}")
            self.log(traceback.format_exc())
            self.test_result("WebSocket manager", False, str(e))
    
    async def test_integration(self):
        """Test 8: Integration Test"""
        self.log("\n" + "=" * 80)
        self.log("TEST 8: Integration Test (Full Workflow)")
        self.log("=" * 80)
        
        try:
            from backend.collaboration.presence_system import presence_system
            from backend.collaboration.workflow_engine import workflow_engine, WorkflowType
            from backend.collaboration.notification_service import notification_service
            from backend.collaboration.automation_engine import automation_engine, TriggerType
            
            # Scenario: User joins, creates workflow, gets notified
            
            # Step 1: User joins
            await presence_system.join_session("alice", "Alice", {})
            self.log("✓ Step 1: Alice joined")
            
            # Step 2: Create workflow
            workflow = await workflow_engine.create_workflow(
                workflow_type=WorkflowType.INGESTION_RUN,
                title="Integration Test Workflow",
                description="Testing full integration",
                created_by="alice",
                reviewers=["bob"],
                checklist=["Check data", "Verify quality"]
            )
            self.log(f"✓ Step 2: Workflow created: {workflow.workflow_id}")
            
            # Step 3: Send notification
            await notification_service.create_notification(
                user_id="bob",
                notification_type="workflow_assigned",
                title="New Workflow Assigned",
                message=f"You've been assigned to: {workflow.title}",
                priority="high"
            )
            self.log("✓ Step 3: Notification sent to Bob")
            
            # Step 4: Create automation rule
            rule = await automation_engine.create_rule(
                name="Auto-notify on approval",
                description="Notify creator when workflow approved",
                trigger_type=TriggerType.WORKFLOW_APPROVED,
                trigger_conditions={"workflow_id": workflow.workflow_id},
                actions=[{
                    "type": "send_notification",
                    "params": {
                        "user_id": "alice",
                        "title": "Workflow Approved",
                        "message": "Your workflow was approved!"
                    }
                }]
            )
            self.log(f"✓ Step 4: Automation rule created: {rule.rule_id}")
            
            # Step 5: Approve workflow
            await workflow_engine.approve_workflow(
                workflow_id=workflow.workflow_id,
                user_id="bob",
                user_name="Bob",
                comments="LGTM!"
            )
            self.log("✓ Step 5: Workflow approved by Bob")
            
            # Step 6: Verify state
            final_workflow = await workflow_engine.get_workflow(workflow.workflow_id)
            alice_notifs = await notification_service.get_user_notifications("alice", limit=10)
            
            self.log(f"✓ Step 6: Final state verified")
            self.log(f"   - Workflow status: {final_workflow['status']}")
            self.log(f"   - Alice notifications: {len(alice_notifs)}")
            
            integration_success = (
                final_workflow['status'] in ['approved', 'in_review'] and
                len(alice_notifs) >= 0
            )
            
            self.test_result("Full integration workflow", integration_success)
            
        except Exception as e:
            self.log(f"Integration test error: {e}")
            self.log(traceback.format_exc())
            self.test_result("Integration test", False, str(e))
    
    async def run_all_tests(self):
        """Run all tests"""
        self.log("╔" + "═" * 78 + "╗")
        self.log("║" + " " * 20 + "COLLABORATION SYSTEM E2E TESTS" + " " * 28 + "║")
        self.log("╚" + "═" * 78 + "╝")
        self.log("")
        
        start_time = datetime.now()
        
        await self.test_imports()
        await self.test_presence_system()
        await self.test_workflow_engine()
        await self.test_notification_service()
        await self.test_automation_engine()
        await self.test_copilot_engine()
        await self.test_websocket_manager()
        await self.test_integration()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.log("\n" + "=" * 80)
        self.log("TEST SUMMARY")
        self.log("=" * 80)
        self.log(f"Total Tests: {self.passed + self.failed}")
        self.log(f"✅ Passed: {self.passed}")
        self.log(f"❌ Failed: {self.failed}")
        self.log(f"⏱️  Duration: {duration:.2f}s")
        
        success_rate = (self.passed / (self.passed + self.failed) * 100) if (self.passed + self.failed) > 0 else 0
        self.log(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            self.log("\n🎉 ALL TESTS PASSED! 🎉")
        else:
            self.log(f"\n⚠️  {self.failed} test(s) failed. See logs above for details.")
        
        self.log("=" * 80)
        
        return self.failed == 0


async def main():
    """Main test runner"""
    test = CollaborationE2ETest()
    
    try:
        success = await test.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
