from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from sqlalchemy import select, and_
import math

if TYPE_CHECKING:
    pass

def _get_models():
    """Lazy import to avoid circular dependency"""
    from .models import CausalEvent, ChatMessage, Task, async_session
    return CausalEvent, ChatMessage, Task, async_session

@dataclass
class CausalNode:
    """Represents an event in the causal graph"""
    event_id: int
    event_type: str  # "message", "task", "execution", "alert", "reflection"
    timestamp: datetime
    user: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash((self.event_id, self.event_type))
    
    def __eq__(self, other):
        if not isinstance(other, CausalNode):
            return False
        return self.event_id == other.event_id and self.event_type == other.event_type

@dataclass
class CausalEdge:
    """Represents a causal relationship between events"""
    source: CausalNode
    target: CausalNode
    strength: float  # 0.0 (weak/uncertain) to 1.0 (certain)
    relationship_type: str  # "triggers", "correlates", "influences", "causes"
    evidence: List[str] = field(default_factory=list)
    
    def __hash__(self):
        return hash((self.source, self.target))

class CausalGraph:
    """Builds and analyzes directed causal graphs from event logs"""
    
    def __init__(self):
        self.nodes: Dict[Tuple[int, str], CausalNode] = {}
        self.edges: Dict[Tuple[CausalNode, CausalNode], CausalEdge] = {}
        self.adjacency_list: Dict[CausalNode, List[CausalEdge]] = defaultdict(list)
        self.reverse_adjacency: Dict[CausalNode, List[CausalEdge]] = defaultdict(list)
    
    async def build_from_events(self, start_date: datetime, end_date: datetime, user: Optional[str] = None) -> int:
        """Construct graph from event log in date range"""
        CausalEvent, ChatMessage, Task, async_session = _get_models()
        
        nodes_added = 0
        edges_added = 0
        
        async with async_session() as session:
            query = select(CausalEvent).where(
                and_(
                    CausalEvent.created_at >= start_date,
                    CausalEvent.created_at <= end_date
                )
            )
            if user:
                query = query.where(CausalEvent.user == user)
            
            result = await session.execute(query.order_by(CausalEvent.created_at))
            causal_events = result.scalars().all()
            
            msg_query = select(ChatMessage).where(
                and_(
                    ChatMessage.created_at >= start_date,
                    ChatMessage.created_at <= end_date
                )
            )
            if user:
                msg_query = msg_query.where(ChatMessage.user == user)
            
            msg_result = await session.execute(msg_query.order_by(ChatMessage.created_at))
            messages = msg_result.scalars().all()
            
            task_query = select(Task).where(
                and_(
                    Task.created_at >= start_date,
                    Task.created_at <= end_date
                )
            )
            if user:
                task_query = task_query.where(Task.user == user)
            
            task_result = await session.execute(task_query.order_by(Task.created_at))
            tasks = task_result.scalars().all()
            
            for msg in messages:
                node = CausalNode(
                    event_id=msg.id,
                    event_type=f"message_{msg.role}",
                    timestamp=msg.created_at,
                    user=msg.user,
                    metadata={"content": msg.content[:100], "role": msg.role}
                )
                self._add_node(node)
                nodes_added += 1
            
            for task in tasks:
                node = CausalNode(
                    event_id=task.id,
                    event_type="task_created",
                    timestamp=task.created_at,
                    user=task.user,
                    metadata={
                        "title": task.title,
                        "status": task.status,
                        "auto_generated": task.auto_generated
                    }
                )
                self._add_node(node)
                nodes_added += 1
                
                if task.completed_at:
                    completion_node = CausalNode(
                        event_id=task.id,
                        event_type="task_completed",
                        timestamp=task.completed_at,
                        user=task.user,
                        metadata={"title": task.title}
                    )
                    self._add_node(completion_node)
                    nodes_added += 1
                    
                    edge = CausalEdge(
                        source=node,
                        target=completion_node,
                        strength=1.0,
                        relationship_type="causes",
                        evidence=["task lifecycle"]
                    )
                    self._add_edge(edge)
                    edges_added += 1
            
            for event in causal_events:
                if event.trigger_message_id and event.response_message_id:
                    trigger_key = (event.trigger_message_id, "message_user")
                    response_key = (event.response_message_id, "message_assistant")
                    
                    trigger_node = self.nodes.get(trigger_key)
                    response_node = self.nodes.get(response_key)
                    
                    if trigger_node and response_node:
                        edge = CausalEdge(
                            source=trigger_node,
                            target=response_node,
                            strength=event.confidence,
                            relationship_type="triggers",
                            evidence=[f"event_type: {event.event_type}"]
                        )
                        self._add_edge(edge)
                        edges_added += 1
            
            temporal_edges = self._infer_temporal_causality()
            edges_added += len(temporal_edges)
            
            pattern_edges = self._infer_pattern_causality()
            edges_added += len(pattern_edges)
        
        print(f"✓ Built causal graph: {nodes_added} nodes, {edges_added} edges")
        return nodes_added
    
    def _add_node(self, node: CausalNode):
        """Add node to graph"""
        key = (node.event_id, node.event_type)
        self.nodes[key] = node
    
    def _add_edge(self, edge: CausalEdge):
        """Add edge to graph"""
        key = (edge.source, edge.target)
        self.edges[key] = edge
        self.adjacency_list[edge.source].append(edge)
        self.reverse_adjacency[edge.target].append(edge)
    
    def _infer_temporal_causality(self) -> List[CausalEdge]:
        """Infer causality from temporal ordering (A before B within time window)"""
        new_edges = []
        time_window = timedelta(minutes=10)
        
        sorted_nodes = sorted(self.nodes.values(), key=lambda n: n.timestamp)
        
        for i, node in enumerate(sorted_nodes):
            if node.event_type == "message_user":
                for j in range(i + 1, len(sorted_nodes)):
                    next_node = sorted_nodes[j]
                    
                    time_diff = next_node.timestamp - node.timestamp
                    if time_diff > time_window:
                        break
                    
                    if next_node.event_type == "task_created" and next_node.user == node.user:
                        if (node, next_node) not in self.edges:
                            strength = self._calculate_temporal_strength(time_diff)
                            edge = CausalEdge(
                                source=node,
                                target=next_node,
                                strength=strength,
                                relationship_type="influences",
                                evidence=[f"temporal proximity: {time_diff.total_seconds()}s"]
                            )
                            self._add_edge(edge)
                            new_edges.append(edge)
        
        return new_edges
    
    def _calculate_temporal_strength(self, time_diff: timedelta) -> float:
        """Calculate causality strength based on time proximity (decay function)"""
        seconds = time_diff.total_seconds()
        decay_rate = 0.001
        strength = math.exp(-decay_rate * seconds)
        return max(0.1, min(0.9, strength))
    
    def _infer_pattern_causality(self) -> List[CausalEdge]:
        """Infer causality from patterns (if A then B happens X% of time)"""
        new_edges = []
        
        user_sequences = defaultdict(list)
        for node in sorted(self.nodes.values(), key=lambda n: n.timestamp):
            user_sequences[node.user].append(node)
        
        for user, sequence in user_sequences.items():
            patterns = self._find_sequential_patterns(sequence)
            
            for pattern_type, occurrence_rate in patterns.items():
                if occurrence_rate > 0.6:
                    event_a_type, event_b_type = pattern_type.split("->")
                    
                    for i, node_a in enumerate(sequence):
                        if node_a.event_type == event_a_type:
                            for node_b in sequence[i+1:i+5]:
                                if node_b.event_type == event_b_type:
                                    if (node_a, node_b) not in self.edges:
                                        edge = CausalEdge(
                                            source=node_a,
                                            target=node_b,
                                            strength=occurrence_rate,
                                            relationship_type="correlates",
                                            evidence=[f"pattern: occurs {occurrence_rate*100:.1f}% of time"]
                                        )
                                        self._add_edge(edge)
                                        new_edges.append(edge)
                                    break
        
        return new_edges
    
    def _find_sequential_patterns(self, sequence: List[CausalNode]) -> Dict[str, float]:
        """Find A->B patterns and their occurrence rates"""
        patterns = defaultdict(lambda: {"count": 0, "opportunities": 0})
        
        for i in range(len(sequence) - 1):
            event_a = sequence[i].event_type
            patterns[event_a]["opportunities"] += 1
            
            for j in range(i + 1, min(i + 5, len(sequence))):
                event_b = sequence[j].event_type
                pattern_key = f"{event_a}->{event_b}"
                patterns[pattern_key]["count"] += 1
        
        occurrence_rates = {}
        for pattern, stats in patterns.items():
            if "->" in pattern and stats["opportunities"] > 0:
                rate = stats["count"] / stats["opportunities"]
                if rate > 0.3:
                    occurrence_rates[pattern] = rate
        
        return occurrence_rates
    
    def find_causes(self, event_id: int, event_type: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """Get all events that led to this one (backward search)"""
        key = (event_id, event_type)
        node = self.nodes.get(key)
        if not node:
            return []
        
        causes = []
        visited = set()
        
        def traverse(current: CausalNode, depth: int):
            if depth > max_depth or current in visited:
                return
            visited.add(current)
            
            for edge in self.reverse_adjacency[current]:
                causes.append({
                    "event_id": edge.source.event_id,
                    "event_type": edge.source.event_type,
                    "timestamp": edge.source.timestamp.isoformat(),
                    "strength": edge.strength,
                    "relationship": edge.relationship_type,
                    "evidence": edge.evidence,
                    "depth": depth,
                    "metadata": edge.source.metadata
                })
                traverse(edge.source, depth + 1)
        
        traverse(node, 0)
        return sorted(causes, key=lambda c: c["strength"], reverse=True)
    
    def find_effects(self, event_id: int, event_type: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """Get all events caused by this one (forward search)"""
        key = (event_id, event_type)
        node = self.nodes.get(key)
        if not node:
            return []
        
        effects = []
        visited = set()
        
        def traverse(current: CausalNode, depth: int):
            if depth > max_depth or current in visited:
                return
            visited.add(current)
            
            for edge in self.adjacency_list[current]:
                effects.append({
                    "event_id": edge.target.event_id,
                    "event_type": edge.target.event_type,
                    "timestamp": edge.target.timestamp.isoformat(),
                    "strength": edge.strength,
                    "relationship": edge.relationship_type,
                    "evidence": edge.evidence,
                    "depth": depth,
                    "metadata": edge.target.metadata
                })
                traverse(edge.target, depth + 1)
        
        traverse(node, 0)
        return sorted(effects, key=lambda e: e["strength"], reverse=True)
    
    def find_path(self, event_a_id: int, event_a_type: str, event_b_id: int, event_b_type: str) -> Optional[List[Dict[str, Any]]]:
        """Find causal chain between two events (BFS)"""
        start_key = (event_a_id, event_a_type)
        end_key = (event_b_id, event_b_type)
        
        start_node = self.nodes.get(start_key)
        end_node = self.nodes.get(end_key)
        
        if not start_node or not end_node:
            return None
        
        queue = deque([(start_node, [])])
        visited = set()
        
        while queue:
            current, path = queue.popleft()
            
            if current in visited:
                continue
            visited.add(current)
            
            if current == end_node:
                return path
            
            for edge in self.adjacency_list[current]:
                new_path = path + [{
                    "from_event_id": edge.source.event_id,
                    "from_event_type": edge.source.event_type,
                    "to_event_id": edge.target.event_id,
                    "to_event_type": edge.target.event_type,
                    "strength": edge.strength,
                    "relationship": edge.relationship_type,
                    "evidence": edge.evidence
                }]
                queue.append((edge.target, new_path))
        
        return None
    
    def calculate_influence(self, event_id: int, event_type: str) -> float:
        """Calculate how much this event affects the system (PageRank-like)"""
        key = (event_id, event_type)
        node = self.nodes.get(key)
        if not node:
            return 0.0
        
        direct_effects = len(self.adjacency_list[node])
        
        total_strength = sum(edge.strength for edge in self.adjacency_list[node])
        
        indirect_effects = 0
        for edge in self.adjacency_list[node]:
            indirect_effects += len(self.adjacency_list[edge.target])
        
        influence = (direct_effects * 1.0) + (total_strength * 0.5) + (indirect_effects * 0.25)
        
        return round(influence, 2)
    
    def detect_cycles(self) -> List[List[Dict[str, Any]]]:
        """Find feedback loops in the graph"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: CausalNode, path: List[CausalNode]):
            visited.add(node)
            rec_stack.add(node)
            
            for edge in self.adjacency_list[node]:
                neighbor = edge.target
                
                if neighbor not in visited:
                    dfs(neighbor, path + [node])
                elif neighbor in rec_stack:
                    cycle_start_idx = path.index(neighbor) if neighbor in path else 0
                    cycle_path = path[cycle_start_idx:] + [node, neighbor]
                    
                    cycle_data = []
                    for i in range(len(cycle_path) - 1):
                        edge_key = (cycle_path[i], cycle_path[i+1])
                        if edge_key in self.edges:
                            e = self.edges[edge_key]
                            cycle_data.append({
                                "from_event_id": e.source.event_id,
                                "from_event_type": e.source.event_type,
                                "to_event_id": e.target.event_id,
                                "to_event_type": e.target.event_type,
                                "strength": e.strength
                            })
                    
                    if cycle_data and cycle_data not in cycles:
                        cycles.append(cycle_data)
            
            rec_stack.remove(node)
        
        for node in self.nodes.values():
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def prune_weak_edges(self, threshold: float = 0.3):
        """Remove low-confidence causal links"""
        edges_to_remove = []
        
        for key, edge in self.edges.items():
            if edge.strength < threshold:
                edges_to_remove.append(key)
        
        for key in edges_to_remove:
            edge = self.edges[key]
            self.adjacency_list[edge.source].remove(edge)
            self.reverse_adjacency[edge.target].remove(edge)
            del self.edges[key]
        
        print(f"✓ Pruned {len(edges_to_remove)} weak edges (threshold: {threshold})")
        return len(edges_to_remove)
    
    def export_for_visualization(self) -> Dict[str, Any]:
        """Export graph to JSON for D3.js/Cytoscape"""
        nodes_data = []
        for node in self.nodes.values():
            nodes_data.append({
                "id": f"{node.event_type}_{node.event_id}",
                "event_id": node.event_id,
                "event_type": node.event_type,
                "timestamp": node.timestamp.isoformat(),
                "user": node.user,
                "metadata": node.metadata,
                "influence": self.calculate_influence(node.event_id, node.event_type)
            })
        
        edges_data = []
        for edge in self.edges.values():
            edges_data.append({
                "source": f"{edge.source.event_type}_{edge.source.event_id}",
                "target": f"{edge.target.event_type}_{edge.target.event_id}",
                "strength": edge.strength,
                "relationship_type": edge.relationship_type,
                "evidence": edge.evidence
            })
        
        return {
            "nodes": nodes_data,
            "edges": edges_data,
            "stats": {
                "total_nodes": len(nodes_data),
                "total_edges": len(edges_data),
                "avg_edge_strength": sum(e["strength"] for e in edges_data) / len(edges_data) if edges_data else 0
            }
        }
    
    def get_most_influential_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get events with highest influence scores"""
        influence_scores = []
        
        for node in self.nodes.values():
            influence = self.calculate_influence(node.event_id, node.event_type)
            if influence > 0:
                influence_scores.append({
                    "event_id": node.event_id,
                    "event_type": node.event_type,
                    "timestamp": node.timestamp.isoformat(),
                    "influence": influence,
                    "metadata": node.metadata
                })
        
        return sorted(influence_scores, key=lambda x: x["influence"], reverse=True)[:limit]

causal_graph = CausalGraph()
