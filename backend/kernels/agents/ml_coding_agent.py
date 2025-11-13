"""
ML Coding Agent
Uses GRACE'S INTERNAL LLM for code generation and understanding

Grace's own reasoning capabilities from:
- Learned code patterns (GitHub mining)
- Programming books ingested
- Constitutional reasoning
- Causal RL decision-making

External APIs only for: research papers, datasets, pre-trained models
NOT for LLM generation (Grace does that herself)
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...transcendence.ml_api_integrator import ml_api_integrator
from ...transcendence.llm_provider_router import llm_router, grace_llm
from ...unified_logger import unified_logger
from ...activity_monitor import activity_monitor

logger = logging.getLogger(__name__)


class MLCodingAgent:
    """
    Coding agent that leverages Grace's INTERNAL LLM for:
    - Code generation
    - Code understanding
    - Bug detection
    - Refactoring suggestions
    - Documentation generation
    """
    
    def __init__(self):
        self.name = "ML Coding Agent (Grace Internal LLM)"
        self.capabilities = [
            'code_generation',
            'code_understanding',
            'bug_detection',
            'refactoring',
            'documentation',
            'test_generation',
            'research'
        ]
        self.active_providers = []
        self.request_count = 0
    
    async def initialize(self):
        """Initialize agent"""
        
        await ml_api_integrator.start()
        self.active_providers = await ml_api_integrator.get_active_providers()
        
        logger.info(f"[ML-CODING-AGENT] Initialized with Grace's internal LLM")
        logger.info(f"[ML-CODING-AGENT] External providers for research: {len(self.active_providers)}")
    
    async def generate_code(
        self,
        description: str,
        language: str = 'python',
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code from natural language description
        Uses Grace's internal LLM (learned from code patterns)
        
        Args:
            description: What the code should do
            language: Programming language
            context: Additional context (existing code, imports, etc.)
        
        Returns:
            Generated code with metadata
        """
        
        self.request_count += 1
        
        # Build prompt
        prompt = f"""Generate {language} code for the following task:

Task: {description}

Requirements:
- Clean, readable code
- Proper error handling
- Comments for complex logic
- Follow {language} best practices
"""
        
        if context:
            prompt += f"\n\nContext:\n{context}"
        
        # Log activity - what Grace is thinking
        await activity_monitor.log_activity(
            activity_type='thinking',
            description=f'Generating {language} code',
            details={'task': description[:100], 'language': language}
        )
        
        # Use Grace's internal LLM (NOT external APIs)
        logger.info(f"[ML-CODING-AGENT] Generating code via Grace's internal LLM (request #{self.request_count})")
        
        result = await llm_router.generate(
            prompt=prompt,
            context=context,
            max_tokens=2000,
            temperature=0.3,  # Lower temperature for code
            allow_external_fallback=False  # Use Grace's own reasoning only
        )
        
        # Log decision
        await unified_logger.log_agentic_spine_decision(
            decision_type='code_generation',
            decision_context={'language': language, 'description': description[:100]},
            chosen_action='use_grace_internal_llm',
            rationale='Generated code using Grace learned patterns',
            actor='ml_coding_agent',
            confidence=0.85,
            risk_score=0.15,
            status='success'
        )
        
        return {
            'code': result.get('response', ''),
            'language': language,
            'provider': 'Grace Internal LLM',
            'model': 'grace_reasoning_engine',
            'description': description,
            'status': 'success',
            'external_api_used': False,
            'source': 'learned_code_patterns'
        }
    
    async def understand_code(
        self,
        code: str,
        language: str = 'python'
    ) -> Dict[str, Any]:
        """
        Analyze and explain code
        Uses Grace's learned code understanding
        
        Args:
            code: Code to analyze
            language: Programming language
        
        Returns:
            Code analysis and explanation
        """
        
        prompt = f"""Analyze this {language} code and provide:

1. High-level purpose: What does this code do?
2. Step-by-step explanation: How does it work?
3. Key algorithms/patterns: What techniques are used?
4. Potential issues: Any bugs, anti-patterns, or improvements?

Code:
```{language}
{code}
```

Provide a comprehensive analysis.
"""
        
        # Use Grace's internal understanding (learned from code patterns)
        result = await llm_router.generate(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.5,
            allow_external_fallback=False
        )
        
        return {
            'analysis': result.get('response', ''),
            'language': language,
            'provider': 'Grace Internal LLM',
            'model': 'grace_reasoning_engine',
            'status': 'success',
            'external_api_used': False
        }
    
    async def detect_bugs(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """
        Detect potential bugs in code
        Uses Grace's learned bug patterns
        """
        
        prompt = f"""Review this {language} code for bugs, issues, and anti-patterns.

Code:
```{language}
{code}
```

Identify:
1. Bugs or errors
2. Security vulnerabilities
3. Performance issues
4. Anti-patterns
5. Best practice violations

Provide specific line-by-line analysis if possible.
"""
        
        # Use Grace's bug detection (learned from code analysis)
        result = await llm_router.generate(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.3,
            allow_external_fallback=False
        )
        
        return {
            'bugs_found': result.get('response', ''),
            'language': language,
            'provider': 'Grace Internal LLM',
            'status': 'success',
            'external_api_used': False
        }
    
    async def suggest_refactoring(
        self,
        code: str,
        language: str = 'python',
        goals: List[str] = None
    ) -> Dict[str, Any]:
        """
        Suggest refactoring improvements
        
        Args:
            code: Code to refactor
            language: Programming language
            goals: Refactoring goals (e.g., ['performance', 'readability'])
        
        Returns:
            Refactoring suggestions
        """
        
        goals_str = ', '.join(goals) if goals else 'readability and maintainability'
        
        prompt = f"""Suggest refactoring improvements for this {language} code.
Focus on: {goals_str}

Code:
```{language}
{code}
```

Provide:
1. Specific improvements needed
2. Refactored code examples
3. Explanation of why each change improves the code
4. Trade-offs to consider
"""
        
        # Use Grace's refactoring knowledge
        result = await llm_router.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.4,
            allow_external_fallback=False
        )
        
        return {
            'suggestions': result.get('response', ''),
            'language': language,
            'goals': goals,
            'provider': 'Grace Internal LLM',
            'status': 'success',
            'external_api_used': False
        }
    
    async def generate_documentation(
        self,
        code: str,
        language: str = 'python',
        doc_style: str = 'docstring'
    ) -> Dict[str, Any]:
        """
        Generate documentation for code
        
        Args:
            code: Code to document
            language: Programming language
            doc_style: Documentation style (docstring, markdown, etc.)
        
        Returns:
            Generated documentation
        """
        
        prompt = f"""Generate {doc_style} documentation for this {language} code:

Code:
```{language}
{code}
```

Include:
1. Function/class purpose and behavior
2. Parameters (types, descriptions)
3. Return values (type, description)
4. Usage examples
5. Notes, warnings, or edge cases
6. Related functions/classes if applicable

Format as proper {language} {doc_style}.
"""
        
        # Use Grace's documentation generation
        result = await llm_router.generate(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.5,
            allow_external_fallback=False
        )
        
        return {
            'documentation': result.get('response', ''),
            'language': language,
            'style': doc_style,
            'provider': 'Grace Internal LLM',
            'status': 'success',
            'external_api_used': False
        }
    
    async def generate_tests(
        self,
        code: str,
        language: str = 'python',
        framework: str = 'pytest'
    ) -> Dict[str, Any]:
        """
        Generate unit tests for code
        
        Args:
            code: Code to test
            language: Programming language
            framework: Test framework (pytest, unittest, jest, etc.)
        
        Returns:
            Generated test code
        """
        
        prompt = f"""Generate {framework} unit tests for this {language} code:

Code:
```{language}
{code}
```

Requirements:
1. Test happy path
2. Test edge cases
3. Test error conditions
4. Good test coverage
5. Clear test names
6. Use {framework} best practices

Generate complete, runnable test code.
"""
        
        result = await llm_router.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.3,
            allow_external_fallback=False
        )
        
        return {
            'tests': result.get('response', ''),
            'language': language,
            'framework': framework,
            'provider': 'Grace Internal LLM',
            'status': 'success',
            'external_api_used': False
        }
    
    async def research_technique(self, technique: str) -> Dict[str, Any]:
        """
        Research ML/coding technique via Papers With Code / arXiv
        This DOES use external API (for research papers)
        
        Args:
            technique: Technique to research (e.g., "transformer architecture")
        
        Returns:
            Research papers and implementations
        """
        
        # External API OK for research
        papers = await ml_api_integrator.search_papers(technique, max_results=10)
        
        return {
            'technique': technique,
            'papers_found': len(papers),
            'papers': papers,
            'source': 'arXiv API (external)',
            'external_api_used': True,  # This is OK - research purposes
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def get_datasets_for_task(self, task: str) -> Dict[str, Any]:
        """
        Get relevant datasets for ML task
        External API OK for dataset discovery
        """
        
        datasets = await ml_api_integrator.get_datasets(task)
        
        return {
            'task': task,
            'datasets_found': len(datasets),
            'datasets': datasets,
            'source': 'Public datasets',
            'external_api_used': False  # Using known public list
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        
        llm_stats = llm_router.get_stats()
        
        return {
            'agent': self.name,
            'total_requests': self.request_count,
            'capabilities': self.capabilities,
            'llm_stats': llm_stats,
            'external_providers': self.active_providers,
            'primary_llm': 'Grace Internal (100% of generation requests)'
        }


# Global instance
ml_coding_agent = MLCodingAgent()
