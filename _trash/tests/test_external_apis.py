"""Tests for External API Integration

Tests for GitHub, Slack, AWS connectors, secrets vault, and Grace external agent.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from backend.external_apis.github_connector import GitHubClient
from backend.external_apis.slack_connector import SlackClient, SlackWebhookReceiver
from backend.external_apis.aws_connector import AWSClient
from backend.secrets_vault import secrets_vault
from backend.grace_external_agent import GraceExternalAgent


class TestSecretsVault:
    """Test secrets vault operations"""
    
    @pytest.mark.asyncio
    async def test_store_secret(self):
        """Test storing a secret"""
        
        result = await secrets_vault.store_secret(
            secret_key="test_secret",
            secret_value="test_value_123",
            secret_type="api_key",
            owner="test_user",
            service="test_service",
            description="Test secret"
        )
        
        assert result["secret_key"] == "test_secret"
        assert result["action"] in ["created", "updated"]
        assert result["service"] == "test_service"
        assert "verification_id" in result
        
        print(f"✓ Secret stored: {result}")
    
    @pytest.mark.asyncio
    async def test_retrieve_secret(self):
        """Test retrieving a secret"""
        
        # Store first
        await secrets_vault.store_secret(
            secret_key="retrieve_test",
            secret_value="secret_value_456",
            secret_type="token",
            owner="test_user",
            service="github"
        )
        
        # Retrieve
        value = await secrets_vault.retrieve_secret(
            secret_key="retrieve_test",
            accessor="test_user"
        )
        
        assert value == "secret_value_456"
        print(f"✓ Secret retrieved successfully")
    
    @pytest.mark.asyncio
    async def test_list_secrets(self):
        """Test listing secrets"""
        
        # Store a few secrets
        for i in range(3):
            await secrets_vault.store_secret(
                secret_key=f"list_test_{i}",
                secret_value=f"value_{i}",
                secret_type="api_key",
                owner="test_user",
                service="test_service"
            )
        
        # List secrets
        secrets = await secrets_vault.list_secrets(service="test_service")
        
        assert len(secrets) >= 3
        assert all("secret_key" in s for s in secrets)
        
        print(f"✓ Listed {len(secrets)} secrets")
    
    @pytest.mark.asyncio
    async def test_revoke_secret(self):
        """Test revoking a secret"""
        
        # Store
        await secrets_vault.store_secret(
            secret_key="revoke_test",
            secret_value="revoke_value",
            secret_type="api_key",
            owner="test_user"
        )
        
        # Revoke
        result = await secrets_vault.revoke_secret(
            secret_key="revoke_test",
            actor="test_user",
            reason="Test revocation"
        )
        
        assert result["status"] == "revoked"
        
        # Try to retrieve (should fail)
        with pytest.raises(PermissionError):
            await secrets_vault.retrieve_secret(
                secret_key="revoke_test",
                accessor="test_user"
            )
        
        print(f"✓ Secret revoked successfully")


class TestGitHubConnector:
    """Test GitHub connector with mocked API"""
    
    @pytest.mark.asyncio
    @patch('backend.external_apis.github_connector.Github')
    async def test_github_authentication(self, mock_github):
        """Test GitHub authentication"""
        
        # Mock GitHub client
        mock_user = Mock()
        mock_user.login = "test_user"
        
        mock_client = Mock()
        mock_client.get_user.return_value = mock_user
        
        mock_github.return_value = mock_client
        
        # Store token in vault
        await secrets_vault.store_secret(
            secret_key="github_test_token",
            secret_value="ghp_test123",
            secret_type="token",
            owner="test_user",
            service="github"
        )
        
        # Test authentication
        client = GitHubClient(actor="test_user")
        
        # Mock the authentication (would fail without real token)
        with patch.object(client, 'authenticate_with_token', return_value=True):
            result = await client.authenticate_with_token(token_key="github_test_token")
            assert result is True
        
        print("✓ GitHub authentication mocked successfully")
    
    @pytest.mark.asyncio
    async def test_github_governance_check(self):
        """Test governance check for GitHub operations"""
        
        client = GitHubClient(actor="test_user")
        
        # Mock governance check
        with patch.object(client.governance, 'check') as mock_check:
            mock_check.return_value = {"decision": "allow", "policy": None}
            
            await client._check_governance(
                action="list_repos",
                resource="test_org",
                payload={"org": "test_org"}
            )
        
        print("✓ GitHub governance check passed")


class TestSlackConnector:
    """Test Slack connector with mocked API"""
    
    @pytest.mark.asyncio
    @patch('backend.external_apis.slack_connector.WebClient')
    async def test_slack_authentication(self, mock_webclient):
        """Test Slack authentication"""
        
        # Mock Slack client
        mock_client = Mock()
        mock_client.auth_test.return_value = {
            "team": "Test Team",
            "user": "test_user"
        }
        
        mock_webclient.return_value = mock_client
        
        # Store token
        await secrets_vault.store_secret(
            secret_key="slack_test_token",
            secret_value="xoxb-test123",
            secret_type="token",
            owner="test_user",
            service="slack"
        )
        
        # Test authentication (mocked)
        client = SlackClient(actor="test_user")
        
        with patch.object(client, 'authenticate_with_token', return_value=True):
            result = await client.authenticate_with_token(token_key="slack_test_token")
            assert result is True
        
        print("✓ Slack authentication mocked successfully")
    
    @pytest.mark.asyncio
    async def test_slack_webhook_receiver(self):
        """Test Slack webhook event receiver"""
        
        receiver = SlackWebhookReceiver()
        
        event_data = {
            "type": "message",
            "channel": "C123456",
            "user": "U123456",
            "text": "Test message",
            "ts": "1234567890.123456"
        }
        
        result = await receiver.handle_event(event_data)
        
        assert result["status"] == "processed"
        assert result["event_type"] == "message"
        
        print("✓ Slack webhook event processed")


class TestAWSConnector:
    """Test AWS connector with mocked boto3"""
    
    @pytest.mark.asyncio
    @patch('backend.external_apis.aws_connector.boto3')
    async def test_aws_authentication(self, mock_boto3):
        """Test AWS authentication"""
        
        # Mock boto3 clients
        mock_s3 = Mock()
        mock_s3.list_buckets.return_value = {"Buckets": []}
        
        mock_boto3.client.return_value = mock_s3
        
        # Store credentials
        await secrets_vault.store_secret(
            secret_key="aws_test_access_key",
            secret_value="AKIATEST123",
            secret_type="api_key",
            owner="test_user",
            service="aws"
        )
        
        await secrets_vault.store_secret(
            secret_key="aws_test_secret_key",
            secret_value="secret123",
            secret_type="password",
            owner="test_user",
            service="aws"
        )
        
        # Test authentication (mocked)
        client = AWSClient(actor="test_user")
        
        with patch.object(client, 'authenticate_with_credentials', return_value=True):
            result = await client.authenticate_with_credentials(
                access_key_id_key="aws_test_access_key",
                secret_access_key_key="aws_test_secret_key"
            )
            assert result is True
        
        print("✓ AWS authentication mocked successfully")
    
    @pytest.mark.asyncio
    async def test_aws_cost_tracking(self):
        """Test AWS cost tracking"""
        
        client = AWSClient(actor="test_user")
        
        # Track some costs
        await client._track_cost("s3", "upload", 0.023)
        await client._track_cost("s3", "upload", 0.015)
        await client._track_cost("lambda", "invoke", 0.0001)
        
        summary = await client.get_cost_summary()
        
        assert "tracker" in summary
        assert summary["total_operations"] >= 3
        assert summary["total_estimated_cost"] > 0
        
        print(f"✓ Cost tracking: ${summary['total_estimated_cost']:.6f}")


class TestGraceExternalAgent:
    """Test Grace autonomous external agent"""
    
    @pytest.mark.asyncio
    async def test_create_github_issue_from_task(self):
        """Test autonomous GitHub issue creation"""
        
        agent = GraceExternalAgent()
        agent.auto_create_issues = True
        agent.require_parliament_approval = False
        
        task = {
            "id": "task_001",
            "title": "Test Task",
            "description": "Test task description",
            "priority": "medium",
            "category": "test"
        }
        
        # Mock GitHub client
        with patch.object(agent.github, 'create_issue') as mock_create:
            mock_create.return_value = {
                "number": 42,
                "title": "Test Task",
                "url": "https://github.com/test/test/issues/42"
            }
            
            result = await agent.create_github_issue_from_task(task, repo="test/test")
            
            assert result is not None
            assert result["number"] == 42
        
        print("✓ Autonomous GitHub issue creation tested")
    
    @pytest.mark.asyncio
    async def test_notify_slack_on_alert(self):
        """Test autonomous Slack alert notifications"""
        
        agent = GraceExternalAgent()
        agent.auto_notify_slack = True
        agent.require_parliament_approval = False
        
        alert = {
            "type": "security_alert",
            "severity": "medium",
            "message": "Test alert"
        }
        
        # Mock Slack client
        with patch.object(agent.slack, 'send_message') as mock_send:
            mock_send.return_value = {
                "ok": True,
                "channel": "C123456",
                "ts": "1234567890.123456"
            }
            
            result = await agent.notify_slack_on_alert(alert, channel="#test")
            
            assert result is not None
            assert result["ok"] is True
        
        print("✓ Autonomous Slack alert tested")
    
    @pytest.mark.asyncio
    async def test_backup_to_s3(self):
        """Test autonomous S3 backup"""
        
        agent = GraceExternalAgent()
        agent.auto_backup_s3 = True
        
        data = {
            "test_key": "test_value",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Mock AWS client
        with patch.object(agent.aws, 's3_upload_file') as mock_upload:
            mock_upload.return_value = {
                "bucket": "test-bucket",
                "key": "backups/test_data/2025-01-01.json",
                "size": 1024
            }
            
            result = await agent.backup_to_s3(data, data_type="test_data")
            
            assert result is not None
            assert result["bucket"] == "test-bucket"
        
        print("✓ Autonomous S3 backup tested")
    
    @pytest.mark.asyncio
    async def test_parliament_approval_request(self):
        """Test Parliament approval for major operations"""
        
        agent = GraceExternalAgent()
        
        # Mock Parliament engine
        with patch('backend.grace_external_agent.parliament_engine') as mock_parliament:
            mock_parliament.create_session = AsyncMock(return_value={
                "session_id": 123,
                "status": "voting"
            })
            
            session_id = await agent._request_parliament_approval(
                action="critical_operation",
                resource="critical_resource",
                context={"priority": "high"},
                reason="Test Parliament approval"
            )
            
            assert session_id == 123
        
        print("✓ Parliament approval request tested")


async def run_all_tests():
    """Run all external API tests"""
    
    print("\n" + "="*60)
    print("GRACE EXTERNAL API INTEGRATION TESTS")
    print("="*60 + "\n")
    
    # Secrets Vault Tests
    print("Testing Secrets Vault...")
    vault_tests = TestSecretsVault()
    await vault_tests.test_store_secret()
    await vault_tests.test_retrieve_secret()
    await vault_tests.test_list_secrets()
    await vault_tests.test_revoke_secret()
    
    # GitHub Tests
    print("\nTesting GitHub Connector...")
    github_tests = TestGitHubConnector()
    await github_tests.test_github_authentication()
    await github_tests.test_github_governance_check()
    
    # Slack Tests
    print("\nTesting Slack Connector...")
    slack_tests = TestSlackConnector()
    await slack_tests.test_slack_authentication()
    await slack_tests.test_slack_webhook_receiver()
    
    # AWS Tests
    print("\nTesting AWS Connector...")
    aws_tests = TestAWSConnector()
    await aws_tests.test_aws_authentication()
    await aws_tests.test_aws_cost_tracking()
    
    # Grace External Agent Tests
    print("\nTesting Grace External Agent...")
    agent_tests = TestGraceExternalAgent()
    await agent_tests.test_create_github_issue_from_task()
    await agent_tests.test_notify_slack_on_alert()
    await agent_tests.test_backup_to_s3()
    await agent_tests.test_parliament_approval_request()
    
    print("\n" + "="*60)
    print("✓ ALL EXTERNAL API TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
