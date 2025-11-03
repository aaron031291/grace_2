"""Code Memory System - Store and Recall Code Patterns

Parses codebases, extracts patterns, and stores them in Grace's memory
for intelligent code completion and generation.
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, select, or_
from sqlalchemy.sql import func
from .models import Base, async_session

class CodePattern(Base):
    """Stored code patterns for recall and generation"""
    __tablename__ = "code_patterns"
    
    id = Column(Integer, primary_key=True)
    pattern_type = Column(String(64), nullable=False)  # function, class, module, snippet
    language = Column(String(32), nullable=False)  # python, go, javascript, etc.
    
    # Pattern content
    name = Column(String(256), nullable=False)
    signature = Column(Text, nullable=True)  # Function signature or class definition
    code_snippet = Column(Text, nullable=False)  # Actual code
    
    # Context
    file_path = Column(String(512), nullable=True)
    project = Column(String(128), nullable=True)
    module = Column(String(256), nullable=True)
    
    # Meta information
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)  # ["authentication", "database", "api"]
    dependencies = Column(JSON, default=list)  # Import statements
    
    # Pattern analysis
    complexity_score = Column(Float, default=0.0)  # Cyclomatic complexity
    lines_of_code = Column(Integer, default=0)
    parameters = Column(JSON, default=list)  # Function parameters
    return_type = Column(String(128), nullable=True)
    
    # Usage tracking
    times_recalled = Column(Integer, default=0)
    times_used = Column(Integer, default=0)
    success_rate = Column(Float, default=1.0)  # How often it was helpful
    
    # Learning
    confidence_score = Column(Float, default=1.0)  # How confident we are in this pattern
    last_validated = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CodeContext(Base):
    """Current coding context and session state"""
    __tablename__ = "code_contexts"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(128), nullable=False)
    user = Column(String(64), nullable=False)
    
    # Current state
    current_file = Column(String(512), nullable=True)
    current_language = Column(String(32), nullable=True)
    cursor_position = Column(JSON, nullable=True)  # {line: int, column: int}
    
    # Intent
    task_description = Column(Text, nullable=True)  # What user is trying to do
    intent = Column(String(128), nullable=True)  # create_function, fix_bug, refactor, etc.
    
    # Context
    open_files = Column(JSON, default=list)
    recent_edits = Column(JSON, default=list)
    active_patterns = Column(JSON, default=list)  # Patterns being used
    
    # Project context
    project_root = Column(String(512), nullable=True)
    project_type = Column(String(64), nullable=True)  # backend, frontend, fullstack
    framework = Column(String(64), nullable=True)  # fastapi, react, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CodeSymbol(Base):
    """Symbol graph entry for deep contextual search."""

    __tablename__ = "code_symbols"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(256), nullable=False, index=True)
    symbol_type = Column(String(64), nullable=False)
    language = Column(String(32), nullable=False)
    file_path = Column(String(512), nullable=False)
    project = Column(String(128))
    signature = Column(Text)
    docstring = Column(Text)
    tags = Column(JSON, default=list)
    references = Column(JSON, default=list)
    meta_data = Column(JSON, default=dict)  # Renamed from metadata (SQLAlchemy reserved)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CodeMemoryEngine:
    """Parse code, extract patterns, store in memory"""
    
    def __init__(self):
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rs': 'rust'
        }
    
    async def parse_codebase(
        self,
        root_path: str,
        project_name: str = "grace_2",
        language_filter: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Parse entire codebase and extract patterns
        
        Args:
            root_path: Root directory to parse
            project_name: Name of the project
            language_filter: Only parse these languages (e.g., ['python'])
        
        Returns:
            Summary of patterns extracted
        """
        
        root = Path(root_path)
        patterns_extracted = {
            'functions': 0,
            'classes': 0,
            'modules': 0,
            'snippets': 0
        }
        
        # Find all code files
        for ext, lang in self.supported_languages.items():
            if language_filter and lang not in language_filter:
                continue
            
            for file_path in root.rglob(f'*{ext}'):
                # Skip common ignore patterns
                if any(skip in str(file_path) for skip in [
                    '__pycache__', 'node_modules', '.git', 'venv', 'env',
                    '.pytest_cache', 'dist', 'build'
                ]):
                    continue
                
                try:
                    patterns = await self.parse_file(file_path, lang, project_name)
                    for pattern_type in patterns:
                        patterns_extracted[pattern_type] += len(patterns[pattern_type])
                except Exception as e:
                    print(f"Error parsing {file_path}: {e}")
        
        return {
            'project': project_name,
            'patterns_extracted': patterns_extracted,
            'total': sum(patterns_extracted.values())
        }
    
    async def parse_file(
        self,
        file_path: Path,
        language: str,
        project: str
    ) -> Dict[str, List]:
        """
        Parse a single file and extract patterns
        
        Args:
            file_path: Path to file
            language: Programming language
            project: Project name
        
        Returns:
            Dict of pattern types and their instances
        """
        
        if language == 'python':
            return await self._parse_python_file(file_path, project)
        elif language in ['javascript', 'typescript']:
            return await self._parse_js_file(file_path, project)
        else:
            # Generic parser for other languages
            return await self._parse_generic_file(file_path, language, project)
    
    async def _parse_python_file(
        self,
        file_path: Path,
        project: str
    ) -> Dict[str, List]:
        """Parse Python file using AST"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {'functions': [], 'classes': [], 'modules': [], 'snippets': []}
        
        functions = []
        classes = []
        
        # Extract imports (dependencies)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Extract functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_pattern = await self._extract_python_function(
                    node, file_path, project, content, imports
                )
                functions.append(func_pattern)
            elif isinstance(node, ast.ClassDef):
                class_pattern = await self._extract_python_class(
                    node, file_path, project, content, imports
                )
                classes.append(class_pattern)

        function_names = [getattr(p, "name", None) for p in functions if getattr(p, "name", None)]
        class_names = [getattr(p, "name", None) for p in classes if getattr(p, "name", None)]

        await self._record_symbol(
            symbol=file_path.stem,
            symbol_type="module",
            language="python",
            file_path=str(file_path),
            project=project,
            signature=f"module {file_path.stem}",
            docstring="",
            tags=list(set(function_names + class_names + imports)),
            references=imports,
            metadata={
                "functions": function_names,
                "classes": class_names,
            },
        )
        
        return {
            'functions': functions,
            'classes': classes,
            'modules': [],
            'snippets': []
        }
    
    async def _extract_python_function(
        self,
        node: ast.FunctionDef,
        file_path: Path,
        project: str,
        full_content: str,
        imports: List[str]
    ) -> CodePattern:
        """Extract Python function as a pattern"""
        
        # Get function source
        source_lines = full_content.split('\n')
        func_lines = source_lines[node.lineno - 1:node.end_lineno]
        code_snippet = '\n'.join(func_lines)
        
        # Build signature
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        signature = f"def {node.name}({', '.join(args)})"
        
        # Extract docstring
        description = ast.get_docstring(node) or ""
        
        # Extract parameters
        parameters = []
        for arg in node.args.args:
            param_info = {"name": arg.arg}
            if arg.annotation:
                try:
                    param_info["type"] = ast.unparse(arg.annotation)
                except:
                    param_info["type"] = "Any"
            parameters.append(param_info)
        
        # Extract return type
        return_type = None
        if node.returns:
            try:
                return_type = ast.unparse(node.returns)
            except:
                return_type = "Any"
        
        # Generate tags from function name and docstring
        tags = self._generate_tags(node.name, description)
        
        # Store pattern
        async with async_session() as session:
            pattern = CodePattern(
                pattern_type="function",
                language="python",
                name=node.name,
                signature=signature,
                code_snippet=code_snippet,
                file_path=str(file_path),
                project=project,
                module=file_path.stem,
                description=description,
                tags=tags,
                dependencies=imports,
                lines_of_code=len(func_lines),
                parameters=parameters,
                return_type=return_type,
                confidence_score=1.0
            )
            
            session.add(pattern)
            await session.commit()
            await session.refresh(pattern)
            
        await self._record_symbol(
            symbol=node.name,
            symbol_type="function",
            language="python",
            file_path=str(file_path),
            project=project,
            signature=signature,
            docstring=description,
            tags=tags,
            references=imports,
            metadata={
                "parameters": parameters,
                "return_type": return_type,
            },
        )

        return pattern
    
    async def _extract_python_class(
        self,
        node: ast.ClassDef,
        file_path: Path,
        project: str,
        full_content: str,
        imports: List[str]
    ) -> CodePattern:
        """Extract Python class as a pattern"""
        
        # Get class source
        source_lines = full_content.split('\n')
        class_lines = source_lines[node.lineno - 1:node.end_lineno]
        code_snippet = '\n'.join(class_lines)
        
        # Build signature
        bases = [ast.unparse(base) for base in node.bases] if node.bases else []
        signature = f"class {node.name}({', '.join(bases)})" if bases else f"class {node.name}"
        
        # Extract docstring
        description = ast.get_docstring(node) or ""
        
        # Generate tags
        tags = self._generate_tags(node.name, description)
        tags.append("class")
        
        # Store pattern
        async with async_session() as session:
            pattern = CodePattern(
                pattern_type="class",
                language="python",
                name=node.name,
                signature=signature,
                code_snippet=code_snippet,
                file_path=str(file_path),
                project=project,
                module=file_path.stem,
                description=description,
                tags=tags,
                dependencies=imports,
                lines_of_code=len(class_lines),
                confidence_score=1.0
            )
            
            session.add(pattern)
            await session.commit()
            await session.refresh(pattern)
            
        await self._record_symbol(
            symbol=node.name,
            symbol_type="class",
            language="python",
            file_path=str(file_path),
            project=project,
            signature=signature,
            docstring=description,
            tags=tags,
            references=imports,
            metadata={
                "bases": bases,
            },
        )

        return pattern
    
    async def _parse_js_file(self, file_path: Path, project: str) -> Dict[str, List]:
        """Parse JavaScript/TypeScript file (basic regex-based)"""
        # TODO: Implement with proper JS parser (esprima, babel, etc.)
        return {'functions': [], 'classes': [], 'modules': [], 'snippets': []}
    
    async def _parse_generic_file(
        self,
        file_path: Path,
        language: str,
        project: str
    ) -> Dict[str, List]:
        """Generic parser for languages without AST support"""
        # TODO: Implement regex-based pattern extraction
        return {'functions': [], 'classes': [], 'modules': [], 'snippets': []}
    
    def _generate_tags(self, name: str, description: str) -> List[str]:
        """Generate tags from name and description"""
        
        tags = []
        
        # Extract from name (snake_case or camelCase)
        name_parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+', name)
        tags.extend([part.lower() for part in name_parts if len(part) > 2])
        
        # Common patterns
        if 'create' in name.lower() or 'new' in name.lower():
            tags.append('creation')
        if 'delete' in name.lower() or 'remove' in name.lower():
            tags.append('deletion')
        if 'update' in name.lower() or 'edit' in name.lower():
            tags.append('modification')
        if 'get' in name.lower() or 'fetch' in name.lower() or 'retrieve' in name.lower():
            tags.append('retrieval')
        if 'api' in name.lower() or 'endpoint' in name.lower():
            tags.append('api')
        if 'test' in name.lower():
            tags.append('testing')
        
        # Extract from description
        if description:
            desc_lower = description.lower()
            if 'auth' in desc_lower:
                tags.append('authentication')
            if 'database' in desc_lower or 'db' in desc_lower:
                tags.append('database')
            if 'api' in desc_lower or 'endpoint' in desc_lower:
                tags.append('api')
            if 'validate' in desc_lower or 'validation' in desc_lower:
                tags.append('validation')
        
        return list(set(tags))  # Remove duplicates
    
    async def _record_symbol(
        self,
        *,
        symbol: str,
        symbol_type: str,
        language: str,
        file_path: str,
        project: Optional[str],
        signature: Optional[str],
        docstring: Optional[str],
        tags: Optional[List[str]],
        references: Optional[List[str]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Upsert symbol entry for deep search."""

        tags = list({t for t in (tags or []) if t})
        references = list({r for r in (references or []) if r})

        async with async_session() as session:
            result = await session.execute(
                select(CodeSymbol).where(
                    CodeSymbol.symbol == symbol,
                    CodeSymbol.file_path == file_path,
                    CodeSymbol.language == language,
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.signature = signature or existing.signature
                existing.docstring = docstring or existing.docstring
                existing.tags = list({*(existing.tags or []), *tags})
                existing.references = references or existing.references
                existing.metadata = metadata or existing.metadata or {}
                existing.project = project or existing.project
            else:
                entry = CodeSymbol(
                    symbol=symbol,
                    symbol_type=symbol_type,
                    language=language,
                    file_path=file_path,
                    project=project,
                    signature=signature,
                    docstring=docstring,
                    tags=tags,
                    references=references,
                    metadata=metadata or {},
                )
                session.add(entry)

            await session.commit()

    async def recall_patterns(
        self,
        intent: str,
        context: Optional[Dict[str, Any]] = None,
        language: str = "python",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recall relevant patterns based on intent and context
        
        Args:
            intent: What the user is trying to do
            context: Current coding context
            language: Programming language
            limit: Maximum patterns to return
        
        Returns:
            List of relevant patterns with confidence scores
        """
        
        # Generate search tags from intent
        search_tags = self._generate_tags(intent, intent)
        
        async with async_session() as session:
            # Build query
            query = select(CodePattern).where(CodePattern.language == language)
            
            # Filter by tags if we have them
            if search_tags:
                conditions = []
                for tag in search_tags:
                    conditions.append(CodePattern.tags.contains([tag]))
                query = query.where(or_(*conditions))
            
            # Order by success rate and times used
            query = query.order_by(
                CodePattern.success_rate.desc(),
                CodePattern.times_used.desc()
            ).limit(limit)
            
            result = await session.execute(query)
            patterns = result.scalars().all()
            
            return [
                {
                    'id': p.id,
                    'name': p.name,
                    'type': p.pattern_type,
                    'signature': p.signature,
                    'code': p.code_snippet,
                    'description': p.description,
                    'tags': p.tags,
                    'confidence': p.confidence_score * p.success_rate,
                    'file_path': p.file_path
                }
                for p in patterns
            ]

    async def deep_search(
        self,
        *,
        query: str,
        language: str = "python",
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Return combined matches from patterns and symbols."""

        search_tags = self._generate_tags(query, query)

        pattern_conditions = [
            CodePattern.name.ilike(f"%{query}%"),
            CodePattern.description.ilike(f"%{query}%"),
        ]
        for tag in search_tags:
            pattern_conditions.append(CodePattern.tags.contains([tag]))

        symbol_conditions = [
            CodeSymbol.symbol.ilike(f"%{query}%"),
            CodeSymbol.docstring.ilike(f"%{query}%"),
        ]
        for tag in search_tags:
            symbol_conditions.append(CodeSymbol.tags.contains([tag]))

        async with async_session() as session:
            pattern_query = select(CodePattern).where(CodePattern.language == language)
            if pattern_conditions:
                pattern_query = pattern_query.where(or_(*pattern_conditions))
            pattern_query = pattern_query.limit(limit)
            pattern_rows = (await session.execute(pattern_query)).scalars().all()

            symbol_query = select(CodeSymbol).where(CodeSymbol.language == language)
            if symbol_conditions:
                symbol_query = symbol_query.where(or_(*symbol_conditions))
            symbol_query = symbol_query.limit(limit)
            symbol_rows = (await session.execute(symbol_query)).scalars().all()

        matches: List[Dict[str, Any]] = []
        for row in pattern_rows:
            matches.append(
                {
                    "type": "pattern",
                    "name": row.name,
                    "symbol_type": row.pattern_type,
                    "file_path": row.file_path,
                    "signature": row.signature,
                    "description": row.description,
                    "tags": row.tags,
                    "score": float(row.success_rate * row.confidence_score),
                }
            )

        for row in symbol_rows:
            matches.append(
                {
                    "type": "symbol",
                    "name": row.symbol,
                    "symbol_type": row.symbol_type,
                    "file_path": row.file_path,
                    "signature": row.signature,
                    "description": row.docstring,
                    "tags": row.tags,
                    "score": 0.75,
                    "metadata": row.metadata,
                }
            )

        matches.sort(key=lambda item: item.get("score", 0), reverse=True)
        return matches[:limit]

code_memory = CodeMemoryEngine()
