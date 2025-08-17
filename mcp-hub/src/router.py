"""
Request Router for MCP Hub
Routes incoming requests to appropriate MCP servers based on capabilities and load
"""

import asyncio
import json
import random
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging
from .registry import ServiceRegistry, ServiceInfo, ServiceStatus

logger = logging.getLogger(__name__)


@dataclass
class RouteRequest:
    """Represents an incoming request to be routed"""
    method: str
    params: Dict[str, Any]
    capability: str = None
    target_service: str = None
    request_id: str = None


@dataclass
class RouteResponse:
    """Response from routing a request"""
    success: bool
    data: Any = None
    error: str = None
    service_name: str = None
    request_id: str = None


class LoadBalancer:
    """Simple load balancing strategies"""
    
    @staticmethod
    def round_robin(services: List[ServiceInfo], state: Dict) -> Optional[ServiceInfo]:
        """Round-robin load balancing"""
        if not services:
            return None
        
        last_index = state.get('last_index', -1)
        next_index = (last_index + 1) % len(services)
        state['last_index'] = next_index
        return services[next_index]
    
    @staticmethod
    def random_choice(services: List[ServiceInfo], state: Dict) -> Optional[ServiceInfo]:
        """Random selection load balancing"""
        return random.choice(services) if services else None
    
    @staticmethod
    def least_connections(services: List[ServiceInfo], state: Dict) -> Optional[ServiceInfo]:
        """Select service with least active connections"""
        if not services:
            return None
        
        connections = state.get('connections', {})
        min_connections = float('inf')
        selected_service = None
        
        for service in services:
            conn_count = connections.get(service.name, 0)
            if conn_count < min_connections:
                min_connections = conn_count
                selected_service = service
        
        return selected_service


class Router:
    """Routes requests to appropriate MCP servers"""
    
    def __init__(self, registry: ServiceRegistry, load_balancer_strategy: str = 'round_robin'):
        self.registry = registry
        self.load_balancer_state = {}
        self.active_connections = {}
        
        # Select load balancing strategy
        self.load_balancer = {
            'round_robin': LoadBalancer.round_robin,
            'random': LoadBalancer.random_choice,
            'least_connections': LoadBalancer.least_connections
        }.get(load_balancer_strategy, LoadBalancer.round_robin)
    
    async def route(self, request: RouteRequest) -> RouteResponse:
        """Route a request to an appropriate MCP server"""
        try:
            # Direct routing to specific service
            if request.target_service:
                service = self.registry.get_service(request.target_service)
                if not service or service.status != ServiceStatus.HEALTHY:
                    return RouteResponse(
                        success=False,
                        error=f"Service {request.target_service} not available",
                        request_id=request.request_id
                    )
                return await self._forward_request(service, request)
            
            # Capability-based routing
            if request.capability:
                services = self.registry.get_services_by_capability(request.capability)
                if not services:
                    return RouteResponse(
                        success=False,
                        error=f"No services available for capability: {request.capability}",
                        request_id=request.request_id
                    )
                
                # Load balance among capable services
                service = self.load_balancer(services, self.load_balancer_state)
                if service:
                    return await self._forward_request(service, request)
            
            # No routing criteria specified
            return RouteResponse(
                success=False,
                error="No target service or capability specified",
                request_id=request.request_id
            )
            
        except Exception as e:
            logger.error(f"Routing error: {e}")
            return RouteResponse(
                success=False,
                error=str(e),
                request_id=request.request_id
            )
    
    async def _forward_request(self, service: ServiceInfo, request: RouteRequest) -> RouteResponse:
        """Forward request to a specific service"""
        # Track active connections
        self.active_connections[service.name] = self.active_connections.get(service.name, 0) + 1
        
        try:
            # Here you would implement the actual forwarding logic
            # For now, we'll simulate it
            logger.info(f"Forwarding request {request.request_id} to {service.name}")
            
            # Simulate request processing
            await asyncio.sleep(0.1)
            
            return RouteResponse(
                success=True,
                data={"message": f"Request processed by {service.name}"},
                service_name=service.name,
                request_id=request.request_id
            )
            
        finally:
            # Decrement active connections
            self.active_connections[service.name] -= 1
    
    def get_routing_stats(self) -> Dict:
        """Get statistics about routing"""
        return {
            "active_connections": dict(self.active_connections),
            "load_balancer_state": dict(self.load_balancer_state),
            "healthy_services": len(self.registry.get_healthy_services()),
            "total_services": len(self.registry.services)
        }
