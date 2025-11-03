"""External API Integration Module

Connectors for GitHub, Slack, AWS with governance and security.
"""

from .github_connector import GitHubClient
from .slack_connector import SlackClient
from .aws_connector import AWSClient

__all__ = ['GitHubClient', 'SlackClient', 'AWSClient']
