"""
Source Graph - Global Context Indexing
Pillar 1: Graph-aware context for coding agent

Maps every module, kernel, OSS model, and dependency into a queryable graph.
Ensures refactors respect dependencies and shared contracts.
"""

import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class SourceNode:
    """Node in the source graph"""
    node_id: str
    node_type: str  # module, class, function, kernel, model_adapter
    name: str
    file_path: str
    line_start: int
    line_end: int
    
    # Metadata
    docstring: Optional[str] = None
    signature: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    
    # For model adapters
    model_capabilities: Optional[Dict[str, Any]] = None
    contract_hash: Optional[str] = None
    
    # Health
    last_modified: Optional[str] = None
    test_coverage: float = 0.0
    trust_score: float = 1.0
    
    # Grace-specific semantic tags
    grace_semantic_type: Optional[str] = None  # kernel, governance_policy, layer1_adapter, oss_model_wrapper, etc.
    grace_layer: Optional[str] = None  # layer1, layer2, layer3
    grace_domain: Optional[str] = None  # cognition, memory, execution, intelligence, etc.
    requires_chaos_test: bool = False
    requires_governance_approval: bool = False
    constitutional_constraints: List[str] = field(default_factory=list)


@dataclass
class SourceEdge:
    """Edge in the source graph (dependency relationship)"""
    source_id: str
    target_id: str
    edge_type: str  # imports, calls, inherits, implements, wraps_model
    weight: float = 1.0
    
    # Context
    file_path: str
    line_number: int


class SourceGraph:
    """
    Global source code graph
    
    Features:
    - AST-based indexing of all Python files
    - Dependency tracking (imports, calls, inheritance)
    - Model adapter registry
    - Kernel boundary detection
    - Contract verification
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.nodes: Dict[str, SourceNode] = {}
        self.edges: List[SourceEdge] = []
        
        # Indexes for fast lookup
        self.file_to_nodes: Dict[str, List[str]] = defaultdict(list)
        self.name_to_nodes: Dict[str, List[str]] = defaultdict(list)
        self.type_to_nodes: Dict[str, List[str]] = defaultdict(list)
        
        # Model adapter registry
        self.model_adapters: Dict[str, str] = {}  # model_name -> node_id
        
        # Statistics
        self.stats = {
            "total_nodes": 0,
            "total_edges": 0,
            "modules": 0,
            "classes": 0,
            "functions": 0,
            "model_adapters": 0,
            "kernels": 0
        }
    
    async def build_graph(self, exclude_patterns: List[str] = None):
        """Build the source graph by analyzing all Python files"""
        
        exclude_patterns = exclude_patterns or [
            "**/node_modules/**",
            "**/.venv/**",
            "**/__pycache__/**",
            "**/tests/**",  # Optionally include tests
            "**/.git/**"
        ]
        
        logger.info(f"[SOURCE GRAPH] Building graph from {self.project_root}")
        
        # Find all Python files
        python_files = []
        for py_file in self.project_root.rglob("*.py"):
            # Check exclusions
            if any(py_file.match(pattern) for pattern in exclude_patterns):
                continue
            python_files.append(py_file)
        
        logger.info(f"[SOURCE GRAPH] Found {len(python_files)} Python files")
        
        # Index each file
        for py_file in python_files:
            await self._index_file(py_file)
        
        # Build edges (second pass for full context)
        await self._build_edges()
        
        # Detect model adapters
        await self._detect_model_adapters()
        
        # Calculate statistics
        self._update_stats()
        
        logger.info(f"[SOURCE GRAPH] Complete: {self.stats}")
        
        return self.stats
    
    async def _index_file(self, file_path: Path):
        """Index a single Python file"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            # Relative path
            rel_path = str(file_path.relative_to(self.project_root))
            
            # Create module node
            module_id = self._make_node_id("module", rel_path)
            module_node = SourceNode(
                node_id=module_id,
                node_type="module",
                name=file_path.stem,
                file_path=rel_path,
                line_start=1,
                line_end=len(source.splitlines()),
                docstring=ast.get_docstring(tree),
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            )
            
            self._add_node(module_node)
            
            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    await self._index_class(node, rel_path, module_id)
                elif isinstance(node, ast.FunctionDef):
                    await self._index_function(node, rel_path, module_id)
            
        except Exception as e:
            logger.error(f"[SOURCE GRAPH] Error indexing {file_path}: {e}")
    
    async def _index_class(self, node: ast.ClassDef, file_path: str, module_id: str):
        """Index a class definition"""
        
        class_id = self._make_node_id("class", f"{file_path}:{node.name}")
        
        # Get base classes
        bases = [self._get_name(base) for base in node.bases]
        
        class_node = SourceNode(
            node_id=class_id,
            node_type="class",
            name=node.name,
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=ast.get_docstring(node),
            signature=f"class {node.name}({', '.join(bases)})",
            dependencies=bases
        )
        
        self._add_node(class_node)
        
        # Link to module
        self.edges.append(SourceEdge(
            source_id=module_id,
            target_id=class_id,
            edge_type="contains",
            file_path=file_path,
            line_number=node.lineno
        ))
    
    async def _index_function(self, node: ast.FunctionDef, file_path: str, parent_id: str):
        """Index a function definition"""
        
        func_id = self._make_node_id("function", f"{file_path}:{node.name}")
        
        # Build signature
        args = [arg.arg for arg in node.args.args]
        signature = f"def {node.name}({', '.join(args)})"
        
        func_node = SourceNode(
            node_id=func_id,
            node_type="function",
            name=node.name,
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=ast.get_docstring(node),
            signature=signature
        )
        
        self._add_node(func_node)
        
        # Link to parent
        self.edges.append(SourceEdge(
            source_id=parent_id,
            target_id=func_id,
            edge_type="contains",
            file_path=file_path,
            line_number=node.lineno
        ))
    
    async def _build_edges(self):
        """Build dependency edges (second pass)"""
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                tree = ast.parse(source, filename=str(py_file))
                rel_path = str(py_file.relative_to(self.project_root))
                
                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._add_import_edge(rel_path, alias.name, node.lineno)
                    
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            self._add_import_edge(rel_path, f"{module}.{alias.name}", node.lineno)
            
            except Exception as e:
                logger.debug(f"[SOURCE GRAPH] Error building edges for {py_file}: {e}")
    
    def _add_import_edge(self, file_path: str, import_name: str, line_number: int):
        """Add an import dependency edge"""
        
        # Find source node
        source_nodes = self.file_to_nodes.get(file_path, [])
        if not source_nodes:
            return
        
        source_id = source_nodes[0]  # Module node
        
        # Find target node
        target_nodes = self.name_to_nodes.get(import_name.split('.')[-1], [])
        
        for target_id in target_nodes:
            self.edges.append(SourceEdge(
                source_id=source_id,
                target_id=target_id,
                edge_type="imports",
                file_path=file_path,
                line_number=line_number
            ))
    
    async def _detect_model_adapters(self):
        """Detect model adapter nodes and apply Grace-specific semantic tagging"""
        
        adapter_keywords = ['adapter', 'wrapper', 'llm', 'model', 'provider']
        kernel_keywords = ['kernel', '_kernel']
        governance_keywords = ['governance', 'policy', 'constitution']
        layer1_keywords = ['boot', 'orchestrator', 'core_kernel']
        
        for node_id, node in self.nodes.items():
            name_lower = node.name.lower()
            path_lower = node.file_path.lower()
            
            # Tag kernels
            if any(kw in name_lower for kw in kernel_keywords) or 'kernels/' in path_lower:
                node.grace_semantic_type = "kernel"
                node.requires_chaos_test = True  # Kernels require chaos testing
                
                # Determine layer
                if 'core_kernel' in name_lower or 'boot' in path_lower:
                    node.grace_layer = "layer1"
                    node.requires_governance_approval = True
                    node.constitutional_constraints.append("preserve_layer1_stability")
            
            # Tag governance policies
            elif any(kw in name_lower for kw in governance_keywords) or 'governance/' in path_lower:
                node.grace_semantic_type = "governance_policy"
                node.grace_layer = "layer2"
                node.requires_governance_approval = True
                node.constitutional_constraints.extend(["protect_governance_decisions", "require_approval_tier_3"])
            
            # Tag model adapters
            elif any(kw in name_lower for kw in adapter_keywords):
                if node.node_type == "class":
                    node.node_type = "model_adapter"
                    node.grace_semantic_type = "oss_model_wrapper"
                    node.grace_layer = "layer2"
                    
                    # Calculate contract hash
                    contract_data = f"{node.signature}:{node.docstring}"
                    node.contract_hash = hashlib.sha256(contract_data.encode()).hexdigest()[:16]
                    
                    # Model wrappers require verification
                    node.requires_governance_approval = True
                    node.constitutional_constraints.extend([
                        "keep_models_verifiable",
                        "preserve_model_compliance"
                    ])
                    
                    # Register
                    self.model_adapters[node.name] = node_id
            
            # Tag Layer 1 adapters
            elif 'layer1' in path_lower or 'l1_' in name_lower:
                node.grace_semantic_type = "layer1_adapter"
                node.grace_layer = "layer1"
                node.requires_chaos_test = True
                node.requires_governance_approval = True
                node.constitutional_constraints.append("preserve_layer1_stability")
            
            # Tag by domain
            if 'cognition/' in path_lower or 'cognitive' in name_lower:
                node.grace_domain = "cognition"
            elif 'memory/' in path_lower or 'memory_' in name_lower:
                node.grace_domain = "memory"
            elif 'execution/' in path_lower or 'executor' in name_lower:
                node.grace_domain = "execution"
            elif 'intelligence/' in path_lower or 'ml_' in name_lower:
                node.grace_domain = "intelligence"
            elif 'agents/' in path_lower or 'agent' in name_lower:
                node.grace_domain = "agentic"
            elif 'self_heal/' in path_lower:
                node.grace_domain = "self_healing"
            
            logger.debug(f"[SOURCE GRAPH] Tagged {node.name}: {node.grace_semantic_type} | {node.grace_layer} | {node.grace_domain}")
    
    def _add_node(self, node: SourceNode):
        """Add node to graph"""
        self.nodes[node.node_id] = node
        
        # Update indexes
        self.file_to_nodes[node.file_path].append(node.node_id)
        self.name_to_nodes[node.name].append(node.node_id)
        self.type_to_nodes[node.node_type].append(node.node_id)
    
    def _make_node_id(self, node_type: str, identifier: str) -> str:
        """Create a unique node ID"""
        return f"{node_type}:{hashlib.md5(identifier.encode()).hexdigest()[:12]}"
    
    def _get_name(self, node: ast.expr) -> str:
        """Extract name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return "Unknown"
    
    def _update_stats(self):
        """Update statistics"""
        self.stats = {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "modules": len(self.type_to_nodes["module"]),
            "classes": len(self.type_to_nodes["class"]),
            "functions": len(self.type_to_nodes["function"]),
            "model_adapters": len(self.model_adapters),
            "kernels": len([n for n in self.nodes.values() if "kernel" in n.name.lower()])
        }
    
    def query_dependencies(self, node_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """Query all dependencies of a node"""
        
        visited = set()
        dependencies = []
        
        def _traverse(nid: str, depth: int):
            if depth > max_depth or nid in visited:
                return
            
            visited.add(nid)
            
            # Find edges where this node is the source
            for edge in self.edges:
                if edge.source_id == nid:
                    target_node = self.nodes.get(edge.target_id)
                    if target_node:
                        dependencies.append({
                            "node": asdict(target_node),
                            "edge_type": edge.edge_type,
                            "depth": depth
                        })
                        _traverse(edge.target_id, depth + 1)
        
        _traverse(node_id, 0)
        
        return {
            "node_id": node_id,
            "dependencies": dependencies,
            "total_dependencies": len(dependencies)
        }
    
    def query_dependents(self, node_id: str) -> List[SourceNode]:
        """Query all nodes that depend on this node"""
        
        dependents = []
        
        for edge in self.edges:
            if edge.target_id == node_id:
                source_node = self.nodes.get(edge.source_id)
                if source_node:
                    dependents.append(source_node)
        
        return dependents
    
    def query_nodes_by_file(self, file_path: str) -> List[SourceNode]:
        """Get all nodes in a file"""
        node_ids = self.file_to_nodes.get(file_path, [])
        return [self.nodes[nid] for nid in node_ids]
    
    def query_model_adapters(self) -> List[SourceNode]:
        """Get all model adapter nodes"""
        return [self.nodes[nid] for nid in self.model_adapters.values()]
    
    def get_context_for_edit(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Get full context needed before editing files
        
        Returns dependencies, dependents, model adapters, and contracts
        """
        
        context = {
            "files": [],
            "all_dependencies": [],
            "all_dependents": [],
            "affected_model_adapters": [],
            "contract_hashes": {}
        }
        
        for file_path in file_paths:
            nodes = self.query_nodes_by_file(file_path)
            
            for node in nodes:
                # Get dependencies
                deps = self.query_dependencies(node.node_id)
                context["all_dependencies"].extend(deps["dependencies"])
                
                # Get dependents
                dependents = self.query_dependents(node.node_id)
                context["all_dependents"].extend(dependents)
                
                # Check if model adapter
                if node.node_type == "model_adapter":
                    context["affected_model_adapters"].append(node)
                    if node.contract_hash:
                        context["contract_hashes"][node.name] = node.contract_hash
        
        context["files"] = file_paths
        
        return context
    
    def export_graph(self, output_path: Path):
        """Export graph to JSON"""
        
        graph_data = {
            "nodes": [asdict(node) for node in self.nodes.values()],
            "edges": [asdict(edge) for edge in self.edges],
            "stats": self.stats,
            "model_adapters": list(self.model_adapters.keys()),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        with open(output_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        logger.info(f"[SOURCE GRAPH] Exported to {output_path}")


# Global source graph instance
_source_graph: Optional[SourceGraph] = None


async def get_source_graph(rebuild: bool = False) -> SourceGraph:
    """Get or build the global source graph"""
    global _source_graph
    
    if _source_graph is None or rebuild:
        project_root = Path(__file__).parent.parent.parent
        _source_graph = SourceGraph(project_root)
        await _source_graph.build_graph()
    
    return _source_graph
