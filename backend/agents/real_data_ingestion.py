"""
Real Data Ingestion Agent
Uses extracted terminology to find and ingest REAL data:
- Documentation pages (full text)
- Code examples (actual files)
- Datasets (real data to test with)
- GitHub repos (working implementations)
- API specs (OpenAPI/Swagger files)
- Libraries (actual source code)
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import aiohttp
import re

logger = logging.getLogger(__name__)


class RealDataIngestion:
    """
    Uses terminology to discover and ingest real, usable data
    Not just snippets - actual documentation, code, datasets, examples
    """
    
    def __init__(self):
        self.ingested_count = 0
        self.documentation_saved = 0
        self.code_examples_saved = 0
        self.datasets_saved = 0
        self.repos_cloned = 0
        self._initialized = False
        
        # Storage locations
        self.data_dir = Path(__file__).parent.parent.parent / "grace_training"
        self.docs_dir = self.data_dir / "documentation"
        self.code_dir = self.data_dir / "code"
        self.datasets_dir = self.data_dir / "datasets"
        self.repos_dir = self.data_dir / "codebases"
        
        # Create directories
        for directory in [self.docs_dir, self.code_dir, self.datasets_dir, self.repos_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize data ingestion system"""
        if self._initialized:
            return
        
        logger.info("[REAL-DATA-INGEST] Initializing real data ingestion system")
        self._initialized = True
    
    async def ingest_from_terms(
        self,
        terms: List[str],
        context: str = "general"
    ) -> Dict[str, Any]:
        """
        Use extracted terms to find and ingest REAL data
        
        Args:
            terms: Technical terms extracted from problem
            context: Context for what Grace is trying to learn
        
        Returns:
            Report of all real data ingested
        """
        # from backend.services.google_search_service import google_search_service
        
        ingestion_report = {
            'terms_used': terms,
            'context': context,
            'documentation_found': [],
            'code_examples_found': [],
            'datasets_found': [],
            'repos_found': [],
            'api_specs_found': [],
            'total_ingested': 0,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"[REAL-DATA-INGEST] Ingestion disabled per user request.")
        return ingestion_report

        # logger.info(f"[REAL-DATA-INGEST] 📥 Ingesting real data for {len(terms)} terms")
        
        # for term in terms[:10]:  # Limit to prevent overload
            logger.info(f"[REAL-DATA-INGEST] Processing term: {term}")
            
            # 1. Find official documentation
            docs = await self._find_official_docs(term, google_search_service)
            if docs:
                ingestion_report['documentation_found'].extend(docs)
            
            # 2. Find code examples
            code = await self._find_code_examples(term, google_search_service)
            if code:
                ingestion_report['code_examples_found'].extend(code)
            
            # 3. Find datasets
            datasets = await self._find_datasets(term, google_search_service)
            if datasets:
                ingestion_report['datasets_found'].extend(datasets)
            
            # 4. Find GitHub repos
            repos = await self._find_github_repos(term)
            if repos:
                ingestion_report['repos_found'].extend(repos)
            
            # 5. Find API specifications
            api_specs = await self._find_api_specs(term, google_search_service)
            if api_specs:
                ingestion_report['api_specs_found'].extend(api_specs)
        
        # Actually download and save the real data
        if ingestion_report['documentation_found']:
            await self._ingest_documentation(ingestion_report['documentation_found'])
        
        if ingestion_report['code_examples_found']:
            await self._ingest_code_examples(ingestion_report['code_examples_found'])
        
        if ingestion_report['datasets_found']:
            await self._ingest_datasets(ingestion_report['datasets_found'])
        
        if ingestion_report['repos_found']:
            await self._ingest_repos(ingestion_report['repos_found'])
        
        ingestion_report['total_ingested'] = (
            len(ingestion_report['documentation_found']) +
            len(ingestion_report['code_examples_found']) +
            len(ingestion_report['datasets_found']) +
            len(ingestion_report['repos_found']) +
            len(ingestion_report['api_specs_found'])
        )
        
        self.ingested_count += ingestion_report['total_ingested']
        
        logger.info(f"[REAL-DATA-INGEST] ✅ Ingested {ingestion_report['total_ingested']} real resources")
        
        return ingestion_report
    
    async def _find_official_docs(
        self,
        term: str,
        search_service
    ) -> List[Dict[str, Any]]:
        """Find official documentation pages for a term"""
        
        # Search for official docs
        queries = [
            f"{term} official documentation",
            f"{term} docs",
            f"{term} reference guide"
        ]
        
        found_docs = []
        
        for query in queries[:2]:  # Limit queries
            try:
                results = await search_service.search(
                    query=query,
                    num_results=3,
                    min_trust_score=0.8  # High trust for docs
                )
                
                for result in results:
                    url = result.get('url', '')
                    # Filter for actual documentation sites
                    if any(doc_domain in url for doc_domain in [
                        'docs.', 'documentation', '.readthedocs.', 'api.', 'developer.'
                    ]):
                        found_docs.append({
                            'term': term,
                            'url': url,
                            'title': result.get('title', ''),
                            'trust_score': result.get('trust_score', 0.8),
                            'type': 'documentation'
                        })
            
            except Exception as e:
                logger.warning(f"[REAL-DATA-INGEST] Doc search failed for {term}: {e}")
        
        return found_docs[:3]  # Top 3 docs
    
    async def _find_code_examples(
        self,
        term: str,
        search_service
    ) -> List[Dict[str, Any]]:
        """Find actual code examples for a term"""
        
        queries = [
            f"{term} code example",
            f"{term} tutorial example code",
            f"how to use {term} python example"
        ]
        
        found_code = []
        
        for query in queries[:2]:
            try:
                results = await search_service.search(
                    query=query,
                    num_results=3
                )
                
                for result in results:
                    url = result.get('url', '')
                    # Prefer sites with actual code
                    if any(code_site in url for code_site in [
                        'github.com', 'stackoverflow.com', 'replit.com', 'gist.github.com'
                    ]):
                        found_code.append({
                            'term': term,
                            'url': url,
                            'title': result.get('title', ''),
                            'type': 'code_example'
                        })
            
            except Exception as e:
                logger.warning(f"[REAL-DATA-INGEST] Code search failed for {term}: {e}")
        
        return found_code[:3]
    
    async def _find_datasets(
        self,
        term: str,
        search_service
    ) -> List[Dict[str, Any]]:
        """Find real datasets related to term"""
        
        queries = [
            f"{term} dataset",
            f"{term} sample data",
            f"{term} test data"
        ]
        
        found_datasets = []
        
        for query in queries[:2]:
            try:
                results = await search_service.search(
                    query=query,
                    num_results=2
                )
                
                for result in results:
                    url = result.get('url', '')
                    # Look for dataset sites
                    if any(data_site in url for data_site in [
                        'kaggle.com', 'data.gov', 'huggingface.co/datasets', 'github.com'
                    ]) or any(ext in url for ext in ['.csv', '.json', '.parquet', '.xlsx']):
                        found_datasets.append({
                            'term': term,
                            'url': url,
                            'title': result.get('title', ''),
                            'type': 'dataset'
                        })
            
            except Exception as e:
                logger.warning(f"[REAL-DATA-INGEST] Dataset search failed for {term}: {e}")
        
        return found_datasets
    
    async def _find_github_repos(
        self,
        term: str
    ) -> List[Dict[str, Any]]:
        """Find GitHub repositories for term"""
        
        # from backend.services.google_search_service import google_search_service
        
        try:
            # results = await google_search_service.search(
            #     query=f"site:github.com {term}",
            #     num_results=3,
            #     min_trust_score=0.9  # GitHub has high trust
            # )
            results = []
            
            repos = []
            for result in results:
                url = result.get('url', '')
                if 'github.com' in url and '/blob/' not in url:  # Repo URL, not file
                    repos.append({
                        'term': term,
                        'url': url,
                        'title': result.get('title', ''),
                        'type': 'github_repo'
                    })
            
            return repos
        
        except Exception as e:
            logger.warning(f"[REAL-DATA-INGEST] GitHub search failed for {term}: {e}")
            return []
    
    async def _find_api_specs(
        self,
        term: str,
        search_service
    ) -> List[Dict[str, Any]]:
        """Find API specifications (OpenAPI, Swagger, etc.)"""
        
        queries = [
            f"{term} API specification",
            f"{term} OpenAPI swagger",
            f"{term} API reference"
        ]
        
        found_specs = []
        
        for query in queries[:2]:
            try:
                results = await search_service.search(
                    query=query,
                    num_results=2
                )
                
                for result in results:
                    url = result.get('url', '')
                    if any(spec_indicator in url.lower() for spec_indicator in [
                        'swagger', 'openapi', 'api', '/spec', '/reference'
                    ]):
                        found_specs.append({
                            'term': term,
                            'url': url,
                            'title': result.get('title', ''),
                            'type': 'api_spec'
                        })
            
            except Exception as e:
                logger.warning(f"[REAL-DATA-INGEST] API spec search failed for {term}: {e}")
        
        return found_specs
    
    async def _ingest_documentation(
        self,
        docs: List[Dict[str, Any]]
    ):
        """Download and save full documentation pages"""
        
        logger.info(f"[REAL-DATA-INGEST] 📄 Downloading {len(docs)} documentation pages...")
        
        for doc in docs:
            try:
                # Download full page content
                async with aiohttp.ClientSession() as session:
                    async with session.get(doc['url'], timeout=10) as response:
                        if response.status == 200:
                            content_type = response.headers.get('Content-Type', '').lower()
                            
                            term_safe = re.sub(r'[^\w\-]', '_', doc['term'])
                            
                            if 'pdf' in content_type or doc['url'].endswith('.pdf'):
                                content_bytes = await response.read()
                                filename = self.docs_dir / f"{term_safe}_documentation.pdf"
                                
                                with open(filename, 'wb') as f:
                                    f.write(content_bytes)
                                
                                logger.info(f"[REAL-DATA-INGEST] ✅ Saved PDF: {filename.name} (binary)")
                            else:
                                content = await response.text()
                                filename = self.docs_dir / f"{term_safe}_documentation.html"
                                
                                with open(filename, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                
                                logger.info(f"[REAL-DATA-INGEST] ✅ Saved doc: {filename.name}")
                            
                            self.documentation_saved += 1
            
            except Exception as e:
                logger.warning(f"[REAL-DATA-INGEST] Failed to download {doc['url']}: {e}")
    
    async def _ingest_code_examples(
        self,
        code_examples: List[Dict[str, Any]]
    ):
        """Download and save actual code examples"""
        
        logger.info(f"[REAL-DATA-INGEST] 💻 Downloading {len(code_examples)} code examples...")
        
        for example in code_examples:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(example['url'], timeout=10) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Extract code blocks if it's HTML
                            if '<code>' in content or '<pre>' in content:
                                from bs4 import BeautifulSoup
                                soup = BeautifulSoup(content, 'html.parser')
                                code_blocks = soup.find_all(['code', 'pre'])
                                content = '\n\n'.join(block.get_text() for block in code_blocks)
                            
                            # Save to file
                            term_safe = re.sub(r'[^\w\-]', '_', example['term'])
                            filename = self.code_dir / f"{term_safe}_example.py"
                            
                            with open(filename, 'w', encoding='utf-8') as f:
                                f.write(f"# Source: {example['url']}\n")
                                f.write(f"# Term: {example['term']}\n\n")
                                f.write(content)
                            
                            self.code_examples_saved += 1
                            logger.info(f"[REAL-DATA-INGEST] ✅ Saved code: {filename.name}")
            
            except Exception as e:
                logger.warning(f"[REAL-DATA-INGEST] Failed to download code from {example['url']}: {e}")
    
    async def _ingest_datasets(
        self,
        datasets: List[Dict[str, Any]]
    ):
        """Download and save actual datasets"""
        
        logger.info(f"[REAL-DATA-INGEST] 📊 Downloading {len(datasets)} datasets...")
        
        for dataset in datasets:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(dataset['url'], timeout=30) as response:
                        if response.status == 200:
                            content = await response.read()
                            
                            # Determine file extension
                            url = dataset['url']
                            ext = '.csv'  # default
                            if '.json' in url:
                                ext = '.json'
                            elif '.parquet' in url:
                                ext = '.parquet'
                            elif '.xlsx' in url:
                                ext = '.xlsx'
                            
                            # Save to file
                            term_safe = re.sub(r'[^\w\-]', '_', dataset['term'])
                            filename = self.datasets_dir / f"{term_safe}_dataset{ext}"
                            
                            with open(filename, 'wb') as f:
                                f.write(content)
                            
                            self.datasets_saved += 1
                            logger.info(f"[REAL-DATA-INGEST] ✅ Saved dataset: {filename.name}")
            
            except Exception as e:
                logger.warning(f"[REAL-DATA-INGEST] Failed to download dataset from {dataset['url']}: {e}")
    
    async def _ingest_repos(
        self,
        repos: List[Dict[str, Any]]
    ):
        """Clone GitHub repositories"""
        
        logger.info(f"[REAL-DATA-INGEST] 🔧 Cloning {len(repos)} GitHub repos...")
        
        for repo in repos:
            try:
                # Extract owner/repo from URL
                url = repo['url']
                match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
                if match:
                    owner, repo_name = match.groups()
                    repo_name = repo_name.replace('.git', '')
                    
                    # Clone (shallow clone to save space)
                    clone_path = self.repos_dir / f"{owner}_{repo_name}"
                    
                    if not clone_path.exists():
                        import subprocess
                        result = subprocess.run(
                            ['git', 'clone', '--depth', '1', url, str(clone_path)],
                            capture_output=True,
                            timeout=60
                        )
                        
                        if result.returncode == 0:
                            self.repos_cloned += 1
                            logger.info(f"[REAL-DATA-INGEST] ✅ Cloned repo: {owner}/{repo_name}")
                        else:
                            logger.warning(f"[REAL-DATA-INGEST] Git clone failed: {result.stderr}")
                    else:
                        logger.info(f"[REAL-DATA-INGEST] Repo already exists: {owner}/{repo_name}")
            
            except Exception as e:
                logger.warning(f"[REAL-DATA-INGEST] Failed to clone {repo['url']}: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get ingestion metrics"""
        return {
            'total_ingested': self.ingested_count,
            'documentation_saved': self.documentation_saved,
            'code_examples_saved': self.code_examples_saved,
            'datasets_saved': self.datasets_saved,
            'repos_cloned': self.repos_cloned,
            'initialized': self._initialized
        }


# Global instance
real_data_ingestion = RealDataIngestion()
