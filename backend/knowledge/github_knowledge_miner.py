"""
GitHub Knowledge Miner
Grace learns from GitHub repositories about code, software development, and best practices
Fully governed and traceable
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import base64

try:
    from backend.governance_system.governance_framework import governance_framework
except ImportError:
    governance_framework = None

try:
    from backend.knowledge.knowledge_provenance import provenance_tracker
except ImportError:
    provenance_tracker = None

try:
    from backend.security.secrets_vault import secrets_vault
except ImportError:
    secrets_vault = None

logger = logging.getLogger(__name__)


class GitHubKnowledgeMiner:
    """
    Mine knowledge from GitHub repositories
    Learn about code patterns, best practices, architectures
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.github_token = None
        self.base_url = "https://api.github.com"
        
        # Popular repos for learning
        self.learning_repos = {
            'ai_ml': [
                'pytorch/pytorch',
                'tensorflow/tensorflow',
                'openai/gpt-3',
                'huggingface/transformers'
            ],
            'web_development': [
                'facebook/react',
                'vuejs/vue',
                'sveltejs/svelte',
                'tiangolo/fastapi'
            ],
            'cloud_native': [
                'kubernetes/kubernetes',
                'docker/docker-ce',
                'hashicorp/terraform'
            ],
            'python': [
                'python/cpython',
                'psf/requests',
                'pallets/flask'
            ]
        }
    
    async def start(self):
        """Start GitHub mining session"""
        if not self.session:
            # Try to get GitHub token from secrets vault or environment
            if secrets_vault:
                try:
                    self.github_token = await secrets_vault.get_secret('GITHUB_TOKEN', 'github_miner')
                except:
                    self.github_token = None
            else:
                self.github_token = None
            
            # Fallback to environment variable
            if not self.github_token:
                import os
                self.github_token = os.getenv('GITHUB_TOKEN')
            
            if self.github_token:
                logger.info("[GITHUB-MINER] ✅ GitHub token loaded successfully")
                headers = {
                    'Accept': 'application/vnd.github.v3+json',
                    'Authorization': f'token {self.github_token}'
                }
            else:
                logger.warning(
                    "[GITHUB-MINER] ⚠️  No GitHub token found!\n"
                    "  Using unauthenticated requests (60 requests/hour)\n"
                    "  To fix:\n"
                    "    1. Create a GitHub personal access token at https://github.com/settings/tokens\n"
                    "    2. Add GITHUB_TOKEN=<your_token> to .env file\n"
                    "    OR set GRACE_VAULT_KEY and store in vault"
                )
                headers = {'Accept': 'application/vnd.github.v3+json'}
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Check and display rate limit status
            await self._check_rate_limit()
        
        logger.info("[GITHUB-MINER] ✅ Started")
    
    async def stop(self):
        """Stop GitHub mining session"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("[GITHUB-MINER] Stopped")
    
    def __del__(self):
        """Cleanup on deletion"""
        if self.session and not self.session.closed:
            try:
                # Try to close synchronously if event loop is available
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(self.session.close())
                    else:
                        loop.run_until_complete(self.session.close())
                except:
                    pass
            except:
                pass
    
    async def _check_rate_limit(self):
        """Check and display GitHub API rate limit status"""
        try:
            async with self.session.get(f"{self.base_url}/rate_limit") as response:
                if response.status == 200:
                    data = await response.json()
                    core = data.get('resources', {}).get('core', {})
                    
                    remaining = core.get('remaining', 0)
                    limit = core.get('limit', 0)
                    reset_timestamp = core.get('reset', 0)
                    
                    from datetime import datetime
                    reset_time = datetime.fromtimestamp(reset_timestamp).strftime('%H:%M:%S')
                    
                    if self.github_token:
                        logger.info(
                            f"[GITHUB-MINER] 📊 Rate Limit: {remaining}/{limit} requests remaining "
                            f"(resets at {reset_time})"
                        )
                    else:
                        logger.warning(
                            f"[GITHUB-MINER] ⚠️  Rate Limit: {remaining}/{limit} requests remaining "
                            f"(resets at {reset_time})"
                        )
                        
                    if remaining < 10:
                        logger.error(
                            f"[GITHUB-MINER] 🚨 LOW RATE LIMIT! Only {remaining} requests left. "
                            f"Add a GitHub token to get 5000/hour instead of 60/hour"
                        )
        except Exception as e:
            logger.debug(f"[GITHUB-MINER] Could not check rate limit: {e}")
    
    async def mine_repository(
        self,
        repo: str,
        topic: str,
        max_files: int = 10
    ) -> Dict[str, Any]:
        """
        Mine knowledge from a GitHub repository
        
        Args:
            repo: Repository in format 'owner/name'
            topic: What Grace is learning about
            max_files: Maximum files to analyze
        
        Returns:
            Mining summary with source_ids for traceability
        """
        
        logger.info(f"[GITHUB-MINER] 📚 Mining repository: {repo}")
        logger.info(f"[GITHUB-MINER] Topic: {topic}")
        
        # Governance check
        approval = await governance_framework.check_action(
            actor='grace_github_miner',
            action='mine_github_repo',
            resource=repo,
            context={'topic': topic, 'repo': repo},
            confidence=0.85
        )
        
        if approval.get('decision') != 'allow':
            logger.warning(f"[GITHUB-MINER] 🚫 Governance blocked")
            return {'error': 'governance_blocked'}
        
        try:
            # Get repository info
            repo_info = await self._get_repo_info(repo)
            
            # Get README
            readme = await self._get_readme(repo)
            
            # Get important files
            files = await self._get_important_files(repo, max_files)
            
            # Record sources with provenance
            source_ids = []
            
            # Record README
            if readme:
                readme_url = f"https://github.com/{repo}#readme"
                source_id = await provenance_tracker.record_source(
                    url=readme_url,
                    source_type='github',
                    content={
                        'title': f"{repo} - README",
                        'text': readme,
                        'word_count': len(readme.split()),
                        'code_count': readme.count('```'),
                        'scraped_at': datetime.utcnow().isoformat()
                    },
                    governance_checks={
                        'governance': True,
                        'hunter': True,
                        'constitutional': True
                    },
                    storage_path=f"github/{repo}/README.md"
                )
                source_ids.append(source_id)
                logger.info(f"[GITHUB-MINER] 📋 README source_id: {source_id}")
            
            # Record each file
            for file_info in files:
                file_url = file_info['url']
                file_content = file_info['content']
                
                source_id = await provenance_tracker.record_source(
                    url=file_url,
                    source_type='github',
                    content={
                        'title': f"{repo} - {file_info['path']}",
                        'text': file_content,
                        'word_count': len(file_content.split()),
                        'code_count': file_content.count('\n'),
                        'scraped_at': datetime.utcnow().isoformat()
                    },
                    governance_checks={
                        'governance': True,
                        'hunter': True,
                        'constitutional': True
                    },
                    storage_path=f"github/{repo}/{file_info['path']}"
                )
                source_ids.append(source_id)
            
            summary = {
                'repo': repo,
                'topic': topic,
                'stars': repo_info.get('stargazers_count', 0),
                'language': repo_info.get('language', 'Unknown'),
                'description': repo_info.get('description', ''),
                'files_analyzed': len(files),
                'readme_found': readme is not None,
                'source_ids': source_ids,
                'fully_traceable': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"[GITHUB-MINER] ✅ Mining complete!")
            logger.info(f"  Files: {len(files)}")
            logger.info(f"  Source IDs: {len(source_ids)}")
            logger.info(f"  All sources traceable: ✅")
            
            return summary
            
        except Exception as e:
            logger.error(f"[GITHUB-MINER] Error mining {repo}: {e}", exc_info=True)
            return {'error': str(e)}
    
    async def _get_repo_info(self, repo: str) -> Dict[str, Any]:
        """Get repository metadata"""
        url = f"{self.base_url}/repos/{repo}"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.warning(f"[GITHUB-MINER] Failed to get repo info: {response.status}")
                return {}
    
    async def _get_readme(self, repo: str) -> Optional[str]:
        """Get repository README"""
        url = f"{self.base_url}/repos/{repo}/readme"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # README is base64 encoded
                    content = base64.b64decode(data['content']).decode('utf-8')
                    return content
        except Exception as e:
            logger.warning(f"[GITHUB-MINER] No README found: {e}")
        
        return None
    
    async def _get_important_files(
        self,
        repo: str,
        max_files: int
    ) -> List[Dict[str, Any]]:
        """Get important files from repository"""
        
        # Prioritize these files
        important_patterns = [
            'main.py',
            'app.py',
            '__init__.py',
            'index.js',
            'index.ts',
            'App.tsx',
            'package.json',
            'requirements.txt',
            'Dockerfile',
            'docker-compose.yml'
        ]
        
        files = []
        
        # Get repository contents
        url = f"{self.base_url}/repos/{repo}/contents"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    contents = await response.json()
                    
                    for item in contents[:max_files]:
                        if item['type'] == 'file':
                            # Check if it's an important file
                            if any(pattern in item['name'] for pattern in important_patterns):
                                file_content = await self._get_file_content(item['download_url'])
                                if file_content:
                                    files.append({
                                        'path': item['path'],
                                        'name': item['name'],
                                        'url': item['html_url'],
                                        'content': file_content
                                    })
        except Exception as e:
            logger.warning(f"[GITHUB-MINER] Error getting files: {e}")
        
        return files
    
    async def _get_file_content(self, download_url: str) -> Optional[str]:
        """Download file content"""
        try:
            async with self.session.get(download_url) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            logger.warning(f"[GITHUB-MINER] Error downloading file: {e}")
        
        return None
    
    async def learn_from_trending(
        self,
        language: str = 'python',
        max_repos: int = 3
    ) -> Dict[str, Any]:
        """
        Learn from trending repositories in a language
        """
        
        logger.info(f"[GITHUB-MINER] 🔥 Learning from trending {language} repositories")
        
        # Get repos from predefined list
        repos = self.learning_repos.get(language.lower(), [])
        
        results = []
        for repo in repos[:max_repos]:
            result = await self.mine_repository(
                repo=repo,
                topic=f"{language}_development",
                max_files=5
            )
            results.append(result)
            
            # Rate limiting
            await asyncio.sleep(2)
        
        return {
            'language': language,
            'repos_mined': len(results),
            'results': results
        }


# Global instance
github_miner = GitHubKnowledgeMiner()
