"""
Load Balancer - Intelligent Traffic Distribution
Distributes requests across service instances using multiple strategies

Strategies:
- Round Robin
- Least Connections
- Least Response Time
- Weighted
- Health-Aware
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    WEIGHTED = "weighted"
    HEALTH_AWARE = "health_aware"


class LoadBalancer:
    """
    Load Balancer for Grace services
    
    Distributes traffic intelligently across service instances
    Integrates with service discovery for dynamic instance list
    """
    
    def __init__(self):
        self.strategy = LoadBalancingStrategy.HEALTH_AWARE
        self.round_robin_counters: Dict[str, int] = {}
        self.connection_counts: Dict[str, int] = {}
        self.weights: Dict[str, float] = {}  # service_id -> weight
        
        # Metrics
        self.total_routed = 0
        self.routing_decisions: Dict[str, int] = {}  # service_id -> count
    
    def select_instance(
        self,
        capability: str,
        instances: List[Any],
        strategy: Optional[LoadBalancingStrategy] = None
    ) -> Optional[Any]:
        """
        Select best instance for request
        
        Args:
            capability: Required capability
            instances: Available service instances
            strategy: Override default strategy
        
        Returns:
            Selected instance or None
        """
        if not instances:
            return None
        
        # Filter healthy instances
        healthy_instances = [
            i for i in instances
            if i.health_status in ["healthy", "degraded"]
        ]
        
        if not healthy_instances:
            # No healthy instances, use all
            healthy_instances = instances
        
        # Select strategy
        strategy = strategy or self.strategy
        
        # Route based on strategy
        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            instance = self._round_robin(capability, healthy_instances)
        
        elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            instance = self._least_connections(healthy_instances)
        
        elif strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            instance = self._least_response_time(healthy_instances)
        
        elif strategy == LoadBalancingStrategy.WEIGHTED:
            instance = self._weighted(healthy_instances)
        
        elif strategy == LoadBalancingStrategy.HEALTH_AWARE:
            instance = self._health_aware(healthy_instances)
        
        else:
            instance = healthy_instances[0]
        
        # Track routing decision
        if instance:
            self.total_routed += 1
            self.routing_decisions[instance.service_id] = \
                self.routing_decisions.get(instance.service_id, 0) + 1
            
            logger.debug(
                f"[LOAD-BALANCER] Routed to {instance.service_id} "
                f"(strategy: {strategy.value})"
            )
        
        return instance
    
    def _round_robin(self, capability: str, instances: List[Any]) -> Any:
        """Round robin selection"""
        if capability not in self.round_robin_counters:
            self.round_robin_counters[capability] = 0
        
        index = self.round_robin_counters[capability] % len(instances)
        self.round_robin_counters[capability] += 1
        
        return instances[index]
    
    def _least_connections(self, instances: List[Any]) -> Any:
        """Select instance with fewest connections"""
        return min(
            instances,
            key=lambda i: self.connection_counts.get(i.service_id, 0)
        )
    
    def _least_response_time(self, instances: List[Any]) -> Any:
        """Select instance with lowest response time"""
        return min(
            instances,
            key=lambda i: i.response_time_ms
        )
    
    def _weighted(self, instances: List[Any]) -> Any:
        """Weighted selection based on instance weights"""
        import random
        
        # Get weights
        total_weight = sum(
            self.weights.get(i.service_id, 1.0)
            for i in instances
        )
        
        if total_weight == 0:
            return instances[0]
        
        # Random weighted selection
        r = random.uniform(0, total_weight)
        cumulative = 0.0
        
        for instance in instances:
            weight = self.weights.get(instance.service_id, 1.0)
            cumulative += weight
            
            if r <= cumulative:
                return instance
        
        return instances[-1]
    
    def _health_aware(self, instances: List[Any]) -> Any:
        """
        Health-aware selection
        Score based on: health, load, response time, failures
        """
        def calculate_score(instance):
            # Health score
            health_score = {
                'healthy': 100,
                'degraded': 50,
                'unhealthy': 10,
                'unknown': 30
            }.get(instance.health_status, 0)
            
            # Load score (inverse - lower load is better)
            load_score = (1.0 - instance.current_load) * 100
            
            # Response time score (inverse - faster is better)
            response_score = max(0, 100 - instance.response_time_ms / 10)
            
            # Failure score (inverse - fewer failures is better)
            failure_score = max(0, 100 - instance.consecutive_failures * 20)
            
            # Weighted combination
            total_score = (
                health_score * 0.4 +
                load_score * 0.3 +
                response_score * 0.2 +
                failure_score * 0.1
            )
            
            return total_score
        
        # Select instance with highest score
        return max(instances, key=calculate_score)
    
    def increment_connections(self, service_id: str):
        """Increment connection count for service"""
        self.connection_counts[service_id] = \
            self.connection_counts.get(service_id, 0) + 1
    
    def decrement_connections(self, service_id: str):
        """Decrement connection count for service"""
        if service_id in self.connection_counts:
            self.connection_counts[service_id] = max(
                0,
                self.connection_counts[service_id] - 1
            )
    
    def set_weight(self, service_id: str, weight: float):
        """Set weight for weighted load balancing"""
        self.weights[service_id] = weight
        logger.info(f"[LOAD-BALANCER] Set weight for {service_id}: {weight}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        return {
            'total_routed': self.total_routed,
            'routing_decisions': self.routing_decisions,
            'active_connections': self.connection_counts,
            'weights': self.weights,
            'strategy': self.strategy.value
        }


# Singleton instance
load_balancer = LoadBalancer()
