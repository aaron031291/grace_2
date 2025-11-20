"""CLI Commands for External API Integration

Command-line interface for GitHub, Slack, AWS, and Secrets operations.
"""

import asyncio
import click
import json
from typing import Optional

from ...backend.external_apis.github_connector import GitHubClient
from ...backend.external_apis.slack_connector import SlackClient
from ...backend.external_apis.aws_connector import AWSClient
from ...backend.secrets_vault import secrets_vault


@click.group()
def external():
    """External API integration commands"""
    pass


# ==================== GitHub Commands ====================

@external.group()
def github():
    """GitHub API operations"""
    pass


@github.command()
@click.argument('repo')
@click.option('--state', default='open', help='Issue state (open/closed/all)')
@click.option('--limit', default=100, help='Maximum issues to retrieve')
def issues(repo: str, state: str, limit: int):
    """List GitHub issues"""
    
    async def _run():
        client = GitHubClient(actor="cli_user")
        await client.authenticate_with_token()
        
        issues = await client.get_issues(repo=repo, state=state, limit=limit)
        
        click.echo(f"\n📋 Issues in {repo} ({state}):\n")
        for issue in issues:
            click.echo(f"  #{issue['number']}: {issue['title']}")
            click.echo(f"    State: {issue['state']} | Created: {issue['created_at']}")
            click.echo(f"    URL: {issue['url']}\n")
        
        click.echo(f"Total: {len(issues)} issues")
    
    asyncio.run(_run())


@github.command()
@click.argument('repo')
@click.option('--title', required=True, help='Issue title')
@click.option('--body', required=True, help='Issue body')
@click.option('--labels', multiple=True, help='Issue labels')
def create_issue(repo: str, title: str, body: str, labels: tuple):
    """Create GitHub issue"""
    
    async def _run():
        client = GitHubClient(actor="cli_user")
        await client.authenticate_with_token()
        
        result = await client.create_issue(
            repo=repo,
            title=title,
            body=body,
            labels=list(labels) if labels else None
        )
        
        click.echo(f"\n✓ Created issue #{result['number']}")
        click.echo(f"  Title: {result['title']}")
        click.echo(f"  URL: {result['url']}")
        click.echo(f"  Verification ID: {result['verification_id']}")
    
    asyncio.run(_run())


@github.command()
@click.option('--org', help='Organization name (optional)')
def repos(org: Optional[str]):
    """List GitHub repositories"""
    
    async def _run():
        client = GitHubClient(actor="cli_user")
        await client.authenticate_with_token()
        
        repos = await client.list_repositories(org=org)
        
        click.echo(f"\n📦 Repositories{' for ' + org if org else ''}:\n")
        for repo in repos:
            click.echo(f"  {repo['full_name']}")
            click.echo(f"    {repo['description'] or 'No description'}")
            click.echo(f"    ⭐ {repo['stars']} | 🍴 {repo['forks']} | 🔧 {repo['language'] or 'N/A'}\n")
        
        click.echo(f"Total: {len(repos)} repositories")
    
    asyncio.run(_run())


@github.command()
@click.argument('repo')
@click.option('--branch', default='main', help='Branch name')
@click.option('--limit', default=50, help='Maximum commits')
def commits(repo: str, branch: str, limit: int):
    """List GitHub commits"""
    
    async def _run():
        client = GitHubClient(actor="cli_user")
        await client.authenticate_with_token()
        
        commits = await client.list_commits(repo=repo, branch=branch, limit=limit)
        
        click.echo(f"\n📝 Commits in {repo}/{branch}:\n")
        for commit in commits:
            click.echo(f"  {commit['sha'][:7]}: {commit['message'].split(chr(10))[0]}")
            click.echo(f"    By {commit['author']} on {commit['date']}\n")
        
        click.echo(f"Total: {len(commits)} commits")
    
    asyncio.run(_run())


# ==================== Slack Commands ====================

@external.group()
def slack():
    """Slack operations"""
    pass


@slack.command()
@click.argument('channel')
@click.argument('message')
def send(channel: str, message: str):
    """Send Slack message"""
    
    async def _run():
        client = SlackClient(actor="cli_user")
        await client.authenticate_with_token()
        
        result = await client.send_message(channel=channel, text=message)
        
        click.echo(f"\n✓ Message sent to {result['channel']}")
        click.echo(f"  Timestamp: {result['ts']}")
        click.echo(f"  Verification ID: {result['verification_id']}")
    
    asyncio.run(_run())


@slack.command()
def channels():
    """List Slack channels"""
    
    async def _run():
        client = SlackClient(actor="cli_user")
        await client.authenticate_with_token()
        
        channels = await client.list_channels()
        
        click.echo("\n📺 Slack Channels:\n")
        for channel in channels:
            privacy = "🔒 Private" if channel['is_private'] else "🌐 Public"
            archived = " (Archived)" if channel['is_archived'] else ""
            click.echo(f"  #{channel['name']} ({channel['id']}) {privacy}{archived}")
            if channel.get('topic'):
                click.echo(f"    Topic: {channel['topic']}")
            click.echo(f"    Members: {channel['num_members']}\n")
        
        click.echo(f"Total: {len(channels)} channels")
    
    asyncio.run(_run())


@slack.command()
@click.argument('channel_id')
@click.option('--limit', default=100, help='Maximum messages')
def history(channel_id: str, limit: int):
    """Get Slack channel history"""
    
    async def _run():
        client = SlackClient(actor="cli_user")
        await client.authenticate_with_token()
        
        messages = await client.get_channel_history(channel=channel_id, limit=limit)
        
        click.echo(f"\n💬 Channel History:\n")
        for msg in messages:
            click.echo(f"  [{msg['ts']}] {msg.get('user', 'Unknown')}: {msg['text'][:100]}")
        
        click.echo(f"\nTotal: {len(messages)} messages")
    
    asyncio.run(_run())


# ==================== AWS Commands ====================

@external.group()
def aws():
    """AWS operations"""
    pass


@aws.group()
def s3():
    """S3 operations"""
    pass


@s3.command()
@click.argument('bucket')
@click.option('--prefix', default='', help='Object prefix')
def ls(bucket: str, prefix: str):
    """List S3 objects"""
    
    async def _run():
        client = AWSClient(actor="cli_user")
        await client.authenticate_with_credentials()
        
        objects = await client.s3_list_objects(bucket=bucket, prefix=prefix)
        
        click.echo(f"\n📁 Objects in s3://{bucket}/{prefix}:\n")
        for obj in objects:
            size_mb = obj['size'] / (1024 * 1024)
            click.echo(f"  {obj['key']}")
            click.echo(f"    Size: {size_mb:.2f} MB | Modified: {obj['last_modified']}\n")
        
        click.echo(f"Total: {len(objects)} objects")
    
    asyncio.run(_run())


@s3.command()
@click.argument('file_path')
@click.argument('bucket')
@click.argument('key')
def upload(file_path: str, bucket: str, key: str):
    """Upload file to S3"""
    
    async def _run():
        client = AWSClient(actor="cli_user")
        await client.authenticate_with_credentials()
        
        result = await client.s3_upload_file(
            bucket=bucket,
            key=key,
            file_path=file_path
        )
        
        click.echo(f"\n✓ Uploaded to s3://{bucket}/{key}")
        click.echo(f"  Size: {result['size'] / (1024 * 1024):.2f} MB")
        click.echo(f"  Estimated cost: ${result['estimated_cost']:.6f}")
        click.echo(f"  Verification ID: {result['verification_id']}")
    
    asyncio.run(_run())


@s3.command()
@click.argument('bucket')
@click.argument('key')
@click.argument('dest_path')
def download(bucket: str, key: str, dest_path: str):
    """Download file from S3"""
    
    async def _run():
        client = AWSClient(actor="cli_user")
        await client.authenticate_with_credentials()
        
        result = await client.s3_download_file(
            bucket=bucket,
            key=key,
            dest_path=dest_path
        )
        
        click.echo(f"\n✓ Downloaded from s3://{bucket}/{key}")
        click.echo(f"  Saved to: {result['dest_path']}")
        click.echo(f"  Size: {result['size'] / (1024 * 1024):.2f} MB")
    
    asyncio.run(_run())


@aws.group()
def lambda_cmd():
    """Lambda operations"""
    pass


@lambda_cmd.command()
def functions():
    """List Lambda functions"""
    
    async def _run():
        client = AWSClient(actor="cli_user")
        await client.authenticate_with_credentials()
        
        functions = await client.lambda_list_functions()
        
        click.echo("\n⚡ Lambda Functions:\n")
        for func in functions:
            click.echo(f"  {func['name']}")
            click.echo(f"    Runtime: {func['runtime']} | Memory: {func['memory_size']}MB")
            click.echo(f"    Timeout: {func['timeout']}s | Size: {func['code_size']} bytes\n")
        
        click.echo(f"Total: {len(functions)} functions")
    
    asyncio.run(_run())


@lambda_cmd.command()
@click.argument('function_name')
@click.argument('payload_json')
def invoke(function_name: str, payload_json: str):
    """Invoke Lambda function"""
    
    async def _run():
        client = AWSClient(actor="cli_user")
        await client.authenticate_with_credentials()
        
        payload = json.loads(payload_json)
        
        result = await client.lambda_invoke_function(
            function_name=function_name,
            payload=payload
        )
        
        click.echo(f"\n✓ Invoked {function_name}")
        click.echo(f"  Status: {result['status_code']}")
        click.echo(f"  Response:\n{json.dumps(result['payload'], indent=2)}")
    
    asyncio.run(_run())


@aws.group()
def ec2():
    """EC2 operations"""
    pass


@ec2.command()
def instances():
    """List EC2 instances"""
    
    async def _run():
        client = AWSClient(actor="cli_user")
        await client.authenticate_with_credentials()
        
        instances = await client.ec2_list_instances()
        
        click.echo("\n💻 EC2 Instances:\n")
        for instance in instances:
            click.echo(f"  {instance['instance_id']} ({instance['instance_type']})")
            click.echo(f"    State: {instance['state']}")
            click.echo(f"    IPs: {instance['private_ip']} / {instance.get('public_ip', 'N/A')}")
            click.echo(f"    Launched: {instance['launch_time']}\n")
        
        click.echo(f"Total: {len(instances)} instances")
    
    asyncio.run(_run())


# ==================== Secrets Commands ====================

@external.group()
def secrets():
    """Secrets vault operations"""
    pass


@secrets.command()
@click.option('--service', help='Filter by service')
def list(service: Optional[str]):
    """List secrets"""
    
    async def _run():
        secrets_list = await secrets_vault.list_secrets(service=service)
        
        click.echo("\n🔐 Secrets Vault:\n")
        for secret in secrets_list:
            status = "✓ Active" if secret['active'] else "❌ Inactive"
            click.echo(f"  {secret['secret_key']} ({secret['secret_type']}) {status}")
            click.echo(f"    Service: {secret['service'] or 'N/A'}")
            click.echo(f"    Owner: {secret['owner']}")
            click.echo(f"    Accessed: {secret['accessed_count']} times")
            if secret.get('description'):
                click.echo(f"    Description: {secret['description']}")
            click.echo()
        
        click.echo(f"Total: {len(secrets_list)} secrets")
    
    asyncio.run(_run())


@secrets.command()
@click.argument('key')
@click.argument('value')
@click.option('--service', help='Service name (github, slack, aws)')
@click.option('--type', 'secret_type', default='api_key', help='Secret type')
@click.option('--description', help='Description')
def store(key: str, value: str, service: Optional[str], secret_type: str, description: Optional[str]):
    """Store secret in vault"""
    
    async def _run():
        result = await secrets_vault.store_secret(
            secret_key=key,
            secret_value=value,
            secret_type=secret_type,
            owner="cli_user",
            service=service,
            description=description
        )
        
        click.echo(f"\n✓ Secret {result['action']}")
        click.echo(f"  Key: {result['secret_key']}")
        click.echo(f"  Service: {result['service']}")
        click.echo(f"  Verification ID: {result['verification_id']}")
    
    asyncio.run(_run())


@secrets.command()
@click.argument('key')
def get(key: str):
    """Retrieve secret (governed)"""
    
    async def _run():
        value = await secrets_vault.retrieve_secret(
            secret_key=key,
            accessor="cli_user"
        )
        
        click.echo(f"\n🔑 Secret: {key}")
        click.echo(f"  Value: {value}")
    
    asyncio.run(_run())


@secrets.command()
@click.argument('key')
@click.option('--reason', default='CLI revocation', help='Revocation reason')
def revoke(key: str, reason: str):
    """Revoke secret"""
    
    async def _run():
        result = await secrets_vault.revoke_secret(
            secret_key=key,
            actor="cli_user",
            reason=reason
        )
        
        click.echo(f"\n✓ Secret revoked: {result['secret_key']}")
        click.echo(f"  Reason: {result['reason']}")
    
    asyncio.run(_run())


if __name__ == '__main__':
    external()
