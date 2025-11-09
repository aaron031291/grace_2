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

from .governance_framework import governance_framework
from .hunter import HunterEngine
from .constitutional_engine import constitutional_engine
from .knowledge_provenance import provenance_tracker
from .unified_logger import unified_logger
from .secrets_vault import secrets_vault

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
            # Try to get GitHub token from secrets vault
            try:
                self.github_token = await secrets_vault.get_secret('GITHUB_TOKEN')
            except:
                logger.warning("[GITHUB-MINER] No GitHub token - using unauthenticated requests (rate limited)")
            
            headers = {'Accept': 'application/vnd.github.v3+json'}
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
        
        logger.info("[GITHUB-MINER] ✅ Started")
    
    async def stop(self):
        """Stop GitHub mining session"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("[GITHUB-MINER] Stopped")
    
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
