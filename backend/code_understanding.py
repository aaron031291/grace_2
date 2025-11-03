"""Code Understanding Engine - Analyze code context and intent"""

import ast
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from sqlalchemy import select, and_
from .models import async_session
from .code_memory import CodePattern, CodeContext, code_memory
from .causal_analyzer import causal_analyzer

# Lazy import to avoid circular dependency  
def _get_meta_loop():
    from .meta_loop_engine import RecommendationApplicator
    return RecommendationApplicator()

class CodeUnderstandingEngine:
    """Understand code context, intent, and suggest next steps"""
    
    def __init__(self):
        self.language_contexts = {
            'python': {
                'file_patterns': ['.py'],
                'keywords': ['def', 'class', 'import', 'async', 'await'],
                'frameworks': ['fastapi', 'django', 'flask', 'sqlalchemy']
            },
            'javascript': {
                'file_patterns': ['.js', '.jsx'],
                'keywords': ['function', 'const', 'let', 'import', 'export'],
                'frameworks': ['react', 'vue', 'express', 'node']
            },
            'typescript': {
                'file_patterns': ['.ts', '.tsx'],
                'keywords': ['interface', 'type', 'function', 'const', 'import'],
                'frameworks': ['react', 'angular', 'nestjs']
            }
        }
    
    async def analyze_current_context(
        self,
        file_path: str,
        cursor_position: Optional[Dict[str, int]] = None,
        file_content: Optional[str] = None,
        session_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Analyze what user is currently editing
        
        Args:
            file_path: Path to current file
            cursor_position: {line: int, column: int}
            file_content: Current file content (if not provided, read from disk)
            session_id: Session identifier
        
        Returns:
            Context analysis with suggestions
        """
        
        path = Path(file_path)
        language = self._detect_language(path)
        
        # Read file content if not provided
        if file_content is None:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except:
                return {'error': 'Could not read file'}
        
        # Analyze file structure
        file_analysis = await self._analyze_file_structure(file_content, language)
        
        # Determine current scope (what function/class user is in)
        current_scope = None
        if cursor_position and language == 'python':
            current_scope = self._find_current_scope_python(
                file_content, 
                cursor_position['line']
            )
        
        # Find related patterns from memory
        related_patterns = []
        if current_scope:
            related_patterns = await code_memory.recall_patterns(
                intent=current_scope['name'],
                language=language,
                limit=5
            )
        
        # Detect frameworks and dependencies
        frameworks = self._detect_frameworks(file_content, language)
        
        # Store/update context
        async with async_session() as session:
            # Check if context exists
            result = await session.execute(
                select(CodeContext).where(
                    and_(
                        CodeContext.session_id == session_id,
                        CodeContext.current_file == str(file_path)
                    )
                )
            )
            context = result.scalar_one_or_none()
            
            if context:
                context.cursor_position = cursor_position
                context.updated_at = datetime.now()
            else:
                context = CodeContext(
                    session_id=session_id,
                    user="default",
                    current_file=str(file_path),
                    current_language=language,
                    cursor_position=cursor_position,
                    framework=frameworks[0] if frameworks else None
                )
                session.add(context)
            
            await session.commit()
        
        return {
            'file_path': str(file_path),
            'language': language,
            'frameworks': frameworks,
            'structure': file_analysis,
            'current_scope': current_scope,
            'related_patterns': related_patterns,
            'cursor_position': cursor_position
        }
    
    async def understand_intent(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse natural language intent into actionable tasks
        
        Args:
            description: Natural language description (e.g., "add user authentication")
            context: Current coding context
        
        Returns:
            Parsed intent with suggested actions
        """
        
        desc_lower = description.lower()
        
        # Detect intent type
        intent_type = self._classify_intent(desc_lower)
        
        # Extract entities (what things are being acted upon)
        entities = self._extract_entities(description)
        
        # Extract actions
        actions = self._extract_actions(desc_lower)
        
        # Find relevant patterns
        patterns = await code_memory.recall_patterns(
            intent=description,
            context=context,
            language=context.get('language', 'python') if context else 'python',
            limit=10
        )
        
        # Generate implementation steps
        steps = await self._generate_implementation_steps(
            intent_type,
            entities,
            actions,
            context
        )
        
        # Use causal reasoning to predict impact
        predicted_impact = await self._predict_code_impact(description, context)
        
        return {
            'intent_type': intent_type,
            'entities': entities,
            'actions': actions,
            'implementation_steps': steps,
            'relevant_patterns': patterns,
            'predicted_impact': predicted_impact,
            'confidence': self._calculate_intent_confidence(intent_type, entities, patterns)
        }
    
    async def suggest_next_steps(
        self,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Suggest what user might want to do next based on current context
        
        Args:
            context: Current coding context
        
        Returns:
            List of suggested next steps
        """
        
        suggestions = []
        
        # Analyze current scope
        if context.get('current_scope'):
            scope = context['current_scope']
            
            # Missing docstring?
            if scope['type'] in ['function', 'class'] and not scope.get('has_docstring'):
                suggestions.append({
                    'type': 'add_docstring',
                    'title': f"Add docstring to {scope['name']}",
                    'priority': 'medium',
                    'code_suggestion': self._generate_docstring_template(scope)
                })
            
            # Missing type hints?
            if scope['type'] == 'function' and context.get('language') == 'python':
                if not scope.get('has_type_hints'):
                    suggestions.append({
                        'type': 'add_type_hints',
                        'title': f"Add type hints to {scope['name']}",
                        'priority': 'low'
                    })
            
            # Function without tests?
            if scope['type'] == 'function' and not scope['name'].startswith('_'):
                test_exists = await self._check_test_exists(
                    scope['name'],
                    context.get('file_path')
                )
                if not test_exists:
                    suggestions.append({
                        'type': 'create_test',
                        'title': f"Create test for {scope['name']}",
                        'priority': 'high'
                    })
        
        # File-level suggestions
        structure = context.get('structure', {})
        
        # Too many functions in one file?
        if structure.get('function_count', 0) > 20:
            suggestions.append({
                'type': 'refactor_split',
                'title': 'Consider splitting this file into smaller modules',
                'priority': 'low',
                'reason': f"File has {structure['function_count']} functions"
            })
        
        # Missing imports for common patterns?
        common_patterns = await self._detect_common_patterns(context)
        for pattern in common_patterns:
            suggestions.append({
                'type': 'use_pattern',
                'title': f"Use {pattern['name']} pattern",
                'priority': 'medium',
                'pattern': pattern
            })
        
        return suggestions
    
    async def find_related_code(
        self,
        pattern: str,
        context: Optional[Dict[str, Any]] = None,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find similar code in codebase
        
        Args:
            pattern: Code pattern or description to search for
            context: Current context
            similarity_threshold: Minimum similarity score
        
        Returns:
            List of related code snippets
        """
        
        # First try exact pattern recall
        patterns = await code_memory.recall_patterns(
            intent=pattern,
            context=context,
            language=context.get('language', 'python') if context else 'python',
            limit=20
        )
        
        # Filter by similarity threshold
        related = [p for p in patterns if p['confidence'] >= similarity_threshold]
        
        # Group by similarity
        grouped = {
            'exact_matches': [r for r in related if r['confidence'] > 0.9],
            'similar': [r for r in related if 0.7 <= r['confidence'] <= 0.9],
            'related': [r for r in related if r['confidence'] < 0.7]
        }
        
        return grouped
    
    def _detect_language(self, path: Path) -> str:
        """Detect language from file extension"""
        ext = path.suffix.lower()
        
        if ext in ['.py']:
            return 'python'
        elif ext in ['.js', '.jsx']:
            return 'javascript'
        elif ext in ['.ts', '.tsx']:
            return 'typescript'
        elif ext in ['.go']:
            return 'go'
        elif ext in ['.rs']:
            return 'rust'
        elif ext in ['.java']:
            return 'java'
        else:
            return 'unknown'
    
    async def _analyze_file_structure(
        self,
        content: str,
        language: str
    ) -> Dict[str, Any]:
        """Analyze file structure"""
        
        if language == 'python':
            return self._analyze_python_structure(content)
        else:
            return self._analyze_generic_structure(content)
    
    def _analyze_python_structure(self, content: str) -> Dict[str, Any]:
        """Analyze Python file structure"""
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {'error': 'Syntax error in file'}
        
        structure = {
            'imports': [],
            'functions': [],
            'classes': [],
            'function_count': 0,
            'class_count': 0,
            'total_lines': len(content.split('\n'))
        }
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    structure['imports'].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    structure['imports'].append(node.module)
        
        # Extract functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                structure['functions'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args]
                })
                structure['function_count'] += 1
            elif isinstance(node, ast.ClassDef):
                structure['classes'].append({
                    'name': node.name,
                    'line': node.lineno
                })
                structure['class_count'] += 1
        
        return structure
    
    def _analyze_generic_structure(self, content: str) -> Dict[str, Any]:
        """Generic structure analysis"""
        
        return {
            'total_lines': len(content.split('\n')),
            'non_empty_lines': len([l for l in content.split('\n') if l.strip()])
        }
    
    def _find_current_scope_python(
        self,
        content: str,
        cursor_line: int
    ) -> Optional[Dict[str, Any]]:
        """Find what function/class the cursor is in"""
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return None
        
        # Find the deepest scope containing cursor_line
        current_scope = None
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    if node.lineno <= cursor_line <= node.end_lineno:
                        # This scope contains the cursor
                        scope_type = 'function' if isinstance(node, ast.FunctionDef) else 'class'
                        has_docstring = ast.get_docstring(node) is not None
                        
                        current_scope = {
                            'type': scope_type,
                            'name': node.name,
                            'line': node.lineno,
                            'end_line': node.end_lineno,
                            'has_docstring': has_docstring
                        }
                        
                        if scope_type == 'function':
                            current_scope['args'] = [arg.arg for arg in node.args.args]
                            current_scope['has_type_hints'] = node.returns is not None
        
        return current_scope
    
    def _detect_frameworks(self, content: str, language: str) -> List[str]:
        """Detect frameworks used in file"""
        
        frameworks = []
        content_lower = content.lower()
        
        if language == 'python':
            framework_patterns = {
                'fastapi': ['from fastapi', 'import fastapi'],
                'django': ['from django', 'import django'],
                'flask': ['from flask', 'import flask'],
                'sqlalchemy': ['from sqlalchemy', 'import sqlalchemy'],
                'pytest': ['import pytest', 'from pytest'],
                'pydantic': ['from pydantic', 'import pydantic']
            }
            
            for framework, patterns in framework_patterns.items():
                if any(p in content_lower for p in patterns):
                    frameworks.append(framework)
        
        return frameworks
    
    def _classify_intent(self, description: str) -> str:
        """Classify intent type"""
        
        if any(word in description for word in ['create', 'add', 'new', 'implement', 'build']):
            return 'create'
        elif any(word in description for word in ['fix', 'bug', 'error', 'issue', 'problem']):
            return 'fix'
        elif any(word in description for word in ['refactor', 'improve', 'optimize', 'clean']):
            return 'refactor'
        elif any(word in description for word in ['test', 'verify', 'validate']):
            return 'test'
        elif any(word in description for word in ['delete', 'remove', 'drop']):
            return 'delete'
        elif any(word in description for word in ['update', 'modify', 'change', 'edit']):
            return 'update'
        else:
            return 'unknown'
    
    def _extract_entities(self, description: str) -> List[str]:
        """Extract entities (nouns) from description"""
        
        # Simple noun extraction (can be improved with NLP)
        words = re.findall(r'\b[a-z_][a-z0-9_]*\b', description.lower())
        
        # Common programming entities
        entity_keywords = [
            'user', 'auth', 'authentication', 'api', 'endpoint', 'route',
            'database', 'model', 'service', 'controller', 'function', 'class',
            'test', 'validation', 'error', 'response', 'request'
        ]
        
        entities = [w for w in words if w in entity_keywords]
        return list(set(entities))
    
    def _extract_actions(self, description: str) -> List[str]:
        """Extract actions (verbs) from description"""
        
        action_verbs = [
            'create', 'add', 'implement', 'build', 'fix', 'update', 'delete',
            'remove', 'refactor', 'test', 'validate', 'verify', 'check',
            'get', 'fetch', 'retrieve', 'save', 'store', 'load'
        ]
        
        words = description.lower().split()
        actions = [w for w in words if w in action_verbs]
        return list(set(actions))
    
    async def _generate_implementation_steps(
        self,
        intent_type: str,
        entities: List[str],
        actions: List[str],
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate implementation steps for intent"""
        
        steps = []
        
        if intent_type == 'create':
            if 'api' in entities or 'endpoint' in entities:
                steps.append({'step': 1, 'action': 'Define route in routes/', 'type': 'code'})
                steps.append({'step': 2, 'action': 'Create request/response models', 'type': 'code'})
                steps.append({'step': 3, 'action': 'Implement endpoint logic', 'type': 'code'})
                steps.append({'step': 4, 'action': 'Add error handling', 'type': 'code'})
                steps.append({'step': 5, 'action': 'Write tests', 'type': 'test'})
            elif 'function' in entities:
                steps.append({'step': 1, 'action': 'Define function signature', 'type': 'code'})
                steps.append({'step': 2, 'action': 'Implement logic', 'type': 'code'})
                steps.append({'step': 3, 'action': 'Add docstring', 'type': 'documentation'})
                steps.append({'step': 4, 'action': 'Write tests', 'type': 'test'})
        
        elif intent_type == 'fix':
            steps.append({'step': 1, 'action': 'Identify error location', 'type': 'analysis'})
            steps.append({'step': 2, 'action': 'Understand root cause', 'type': 'analysis'})
            steps.append({'step': 3, 'action': 'Implement fix', 'type': 'code'})
            steps.append({'step': 4, 'action': 'Add test to prevent regression', 'type': 'test'})
        
        return steps
    
    async def _predict_code_impact(
        self,
        description: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Predict impact of code change using causal reasoning"""
        
        # Use causal analyzer to predict impact
        impact = {
            'affected_files': [],
            'risk_level': 'low',
            'requires_testing': True,
            'breaking_change': False
        }
        
        # Detect potential breaking changes
        if any(word in description.lower() for word in ['remove', 'delete', 'deprecate']):
            impact['breaking_change'] = True
            impact['risk_level'] = 'high'
        
        # Detect scope
        if any(word in description.lower() for word in ['refactor', 'restructure', 'migrate']):
            impact['risk_level'] = 'medium'
            impact['affected_files'] = ['multiple']
        
        return impact
    
    def _calculate_intent_confidence(
        self,
        intent_type: str,
        entities: List[str],
        patterns: List[Dict]
    ) -> float:
        """Calculate confidence in intent understanding"""
        
        confidence = 0.5  # Base confidence
        
        if intent_type != 'unknown':
            confidence += 0.2
        
        if len(entities) > 0:
            confidence += 0.1 * min(len(entities), 3)
        
        if len(patterns) > 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    async def _check_test_exists(self, function_name: str, file_path: Optional[str]) -> bool:
        """Check if test exists for function"""
        
        from sqlalchemy import select
        
        test_name = f"test_{function_name}"
        
        async with async_session() as session:
            result = await session.execute(
                select(CodePattern).where(CodePattern.name == test_name)
            )
            return result.scalar_one_or_none() is not None
    
    async def _detect_common_patterns(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect opportunities to use common patterns"""
        
        # This would analyze the code and suggest design patterns
        return []
    
    def _generate_docstring_template(self, scope: Dict[str, Any]) -> str:
        """Generate docstring template"""
        
        if scope['type'] == 'function':
            template = f'''"""
Summary of {scope['name']}

Args:
'''
            for arg in scope.get('args', []):
                if arg != 'self':
                    template += f"    {arg}: Description\n"
            
            template += """
Returns:
    Description of return value
"""
            template += '"""'
            return template
        
        elif scope['type'] == 'class':
            return f'''"""
{scope['name']} class

Attributes:
    Add attributes here
"""'''
        
        return '"""Add description"""'

code_understanding = CodeUnderstandingEngine()
