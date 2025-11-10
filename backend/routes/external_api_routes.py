"""External API Routes

FastAPI routes for GitHub, Slack, AWS, and Secrets Vault operations.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from ..external_apis.github_connector import GitHubClient
from ..external_apis.slack_connector import SlackClient, SlackWebhookReceiver
from ..external_apis.aws_connector import AWSClient
from ..secrets_vault import secrets_vault
from ..auth import get_current_user
=======
from ..schemas_extended import (
    GitHubIssueResponse, GitHubReposResponse, GitHubRepoIssuesResponse,
    GitHubPRResponse, GitHubCommitsResponse, SlackMessageResponse,
    SlackChannelsResponse, SlackHistoryResponse, AWS_S3UploadResponse,
    AWS_S3DownloadResponse, AWS_S3ListResponse, AWS_LambdaInvokeResponse,
    AWS_LambdaListResponse, AWS_EC2InstancesResponse, AWS_EC2InstanceStatusResponse,
    AWS_CostsResponse, SecretsListResponse, SecretResponse, SuccessResponse
)
>>>>>>> origin/main

router = APIRouter(prefix="/api/external", tags=["External APIs"])


# ==================== Request/Response Models ====================

class GitHubIssueCreate(BaseModel):
    repo: str
    title: str
    body: str
    labels: Optional[List[str]] = None


class GitHubPRCreate(BaseModel):
    repo: str
    title: str
    body: str
    head: str
    base: str = "main"


class GitHubCommentCreate(BaseModel):
    repo: str
    issue_number: int
    comment: str


class SlackMessage(BaseModel):
    channel: str
    text: str
    thread_ts: Optional[str] = None


class SlackFileUpload(BaseModel):
    channel: str
    file_path: str
    title: Optional[str] = None
    initial_comment: Optional[str] = None


class S3Upload(BaseModel):
    bucket: str
    key: str
    file_path: str
    metadata: Optional[Dict[str, str]] = None


class S3Download(BaseModel):
    bucket: str
    key: str
    dest_path: str


class LambdaInvoke(BaseModel):
    function_name: str
    payload: Dict[str, Any]
    invocation_type: str = "RequestResponse"


class SecretCreate(BaseModel):
    secret_key: str
    secret_value: str
    secret_type: str
    service: Optional[str] = None
    description: Optional[str] = None
    expires_in_days: Optional[int] = None
    rotation_days: Optional[int] = None


# ==================== GitHub Routes ====================

<<<<<<< HEAD
@router.post("/github/issues")
async def create_github_issue(
    data: GitHubIssueCreate,
    user: dict = Depends(get_current_user)
):
    """Create GitHub issue"""
    try:
        client = GitHubClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_token()
        
        result = await client.create_issue(
            repo=data.repo,
            title=data.title,
            body=data.body,
            labels=data.labels
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/github/repos")
async def list_github_repos(
    org: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """List GitHub repositories"""
    try:
        client = GitHubClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_token()
        
        repos = await client.list_repositories(org=org)
        
        return {"repos": repos, "count": len(repos)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/github/repos/{owner}/{repo}/issues")
async def get_github_issues(
    owner: str,
    repo: str,
    state: str = "open",
    limit: int = 100,
    user: dict = Depends(get_current_user)
):
    """Get GitHub issues"""
    try:
        client = GitHubClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_token()
        
        full_repo = f"{owner}/{repo}"
        issues = await client.get_issues(repo=full_repo, state=state, limit=limit)
        
        return {"issues": issues, "count": len(issues)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/github/pr")
async def create_github_pr(
    data: GitHubPRCreate,
    user: dict = Depends(get_current_user)
):
    """Create GitHub pull request"""
    try:
        client = GitHubClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_token()
        
        result = await client.create_pr(
            repo=data.repo,
            title=data.title,
            body=data.body,
            head=data.head,
            base=data.base
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/github/repos/{owner}/{repo}/commits")
async def list_github_commits(
    owner: str,
    repo: str,
    branch: str = "main",
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    """List GitHub commits"""
    try:
        client = GitHubClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_token()
        
        full_repo = f"{owner}/{repo}"
        commits = await client.list_commits(repo=full_repo, branch=branch, limit=limit)
        
        return {"commits": commits, "count": len(commits)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/github/comment")
async def create_github_comment(
    data: GitHubCommentCreate,
    user: dict = Depends(get_current_user)
):
    """Create GitHub comment"""
    try:
        client = GitHubClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_token()
        
        result = await client.create_comment(
            repo=data.repo,
            issue_number=data.issue_number,
            comment=data.comment
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Slack Routes ====================

@router.post("/slack/message")
async def send_slack_message(
    data: SlackMessage,
    user: dict = Depends(get_current_user)
):
    """Send Slack message"""
    try:
        client = SlackClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_token()
        
        result = await client.send_message(
            channel=data.channel,
            text=data.text,
            thread_ts=data.thread_ts
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/slack/channels")
async def list_slack_channels(
    limit: int = 100,
    user: dict = Depends(get_current_user)
):
    """List Slack channels"""
    try:
        client = SlackClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_token()
        
        channels = await client.list_channels(limit=limit)
        
        return {"channels": channels, "count": len(channels)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/slack/channels/{channel_id}/history")
async def get_slack_channel_history(
    channel_id: str,
    limit: int = 100,
    user: dict = Depends(get_current_user)
):
    """Get Slack channel history"""
    try:
        client = SlackClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_token()
        
        messages = await client.get_channel_history(channel=channel_id, limit=limit)
        
        return {"messages": messages, "count": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/slack/upload")
async def upload_slack_file(
    data: SlackFileUpload,
    user: dict = Depends(get_current_user)
):
    """Upload file to Slack"""
    try:
        client = SlackClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_token()
        
        result = await client.upload_file(
            channel=data.channel,
            file_path=data.file_path,
            title=data.title,
            initial_comment=data.initial_comment
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/slack/webhook")
async def slack_webhook_handler(event_data: Dict[str, Any] = Body(...)):
    """Handle incoming Slack webhook events"""
    try:
        receiver = SlackWebhookReceiver()
        result = await receiver.handle_event(event_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== AWS Routes ====================

@router.post("/aws/s3/upload")
async def aws_s3_upload(
    data: S3Upload,
    user: dict = Depends(get_current_user)
):
    """Upload file to S3"""
    try:
        client = AWSClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_credentials()
        
        result = await client.s3_upload_file(
            bucket=data.bucket,
            key=data.key,
            file_path=data.file_path,
            metadata=data.metadata
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/aws/s3/download")
async def aws_s3_download(
    data: S3Download,
    user: dict = Depends(get_current_user)
):
    """Download file from S3"""
    try:
        client = AWSClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_credentials()
        
        result = await client.s3_download_file(
            bucket=data.bucket,
            key=data.key,
            dest_path=data.dest_path
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/aws/s3/list")
async def aws_s3_list(
    bucket: str,
    prefix: str = "",
    max_keys: int = 1000,
    user: dict = Depends(get_current_user)
):
    """List S3 objects"""
    try:
        client = AWSClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_credentials()
        
        objects = await client.s3_list_objects(bucket=bucket, prefix=prefix, max_keys=max_keys)
        
        return {"objects": objects, "count": len(objects)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/aws/s3/delete")
async def aws_s3_delete(
    bucket: str,
    key: str,
    user: dict = Depends(get_current_user)
):
    """Delete S3 object"""
    try:
        client = AWSClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_credentials()
        
        result = await client.s3_delete_object(bucket=bucket, key=key)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/aws/lambda/invoke")
async def aws_lambda_invoke(
    data: LambdaInvoke,
    user: dict = Depends(get_current_user)
):
    """Invoke AWS Lambda function"""
    try:
        client = AWSClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_credentials()
        
        result = await client.lambda_invoke_function(
            function_name=data.function_name,
            payload=data.payload,
            invocation_type=data.invocation_type
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/aws/lambda/functions")
async def aws_lambda_list(
    max_items: int = 50,
    user: dict = Depends(get_current_user)
):
    """List Lambda functions"""
    try:
        client = AWSClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_credentials()
        
        functions = await client.lambda_list_functions(max_items=max_items)
        
        return {"functions": functions, "count": len(functions)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/aws/ec2/instances")
async def aws_ec2_list(user: dict = Depends(get_current_user)):
    """List EC2 instances"""
    try:
        client = AWSClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_credentials()
        
        instances = await client.ec2_list_instances()
        
        return {"instances": instances, "count": len(instances)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/aws/ec2/instances/{instance_id}/status")
async def aws_ec2_status(
    instance_id: str,
    user: dict = Depends(get_current_user)
):
    """Get EC2 instance status"""
    try:
        client = AWSClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_credentials()
        
        status = await client.ec2_get_instance_status(instance_id=instance_id)
        
        return status
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/aws/costs")
async def aws_cost_summary(user: dict = Depends(get_current_user)):
    """Get AWS cost tracking summary"""
    try:
        client = AWSClient(actor=user.get("username", "unknown"))
        await client.authenticate_with_credentials()
        
        summary = await client.get_cost_summary()
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Secrets Vault Routes ====================

@router.get("/secrets")
async def list_secrets(
    service: Optional[str] = None,
    include_inactive: bool = False,
    user: dict = Depends(get_current_user)
):
    """List secrets (metadata only)"""
    try:
        secrets = await secrets_vault.list_secrets(
            owner=user.get("username"),
            service=service,
            include_inactive=include_inactive
        )
        
        return {"secrets": secrets, "count": len(secrets)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/secrets")
async def create_secret(
    data: SecretCreate,
    user: dict = Depends(get_current_user)
):
    """Store secret in vault"""
    try:
        result = await secrets_vault.store_secret(
            secret_key=data.secret_key,
            secret_value=data.secret_value,
            secret_type=data.secret_type,
            owner=user.get("username", "unknown"),
            service=data.service,
            description=data.description,
            expires_in_days=data.expires_in_days,
            rotation_days=data.rotation_days
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/secrets/{secret_key}")
async def get_secret(
    secret_key: str,
    user: dict = Depends(get_current_user)
):
    """Retrieve secret from vault (governed)"""
    try:
        secret_value = await secrets_vault.retrieve_secret(
            secret_key=secret_key,
            accessor=user.get("username", "unknown")
        )
        
        return {"secret_key": secret_key, "secret_value": secret_value}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/secrets/{secret_key}")
async def revoke_secret(
    secret_key: str,
    reason: str = "User requested revocation",
    user: dict = Depends(get_current_user)
):
    """Revoke secret"""
    try:
        result = await secrets_vault.revoke_secret(
            secret_key=secret_key,
            actor=user.get("username", "unknown"),
            reason=reason
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
