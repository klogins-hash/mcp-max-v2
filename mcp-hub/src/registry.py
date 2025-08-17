"""
Service Registry for MCP Servers
Handles service discovery, registration, and health monitoring
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """Information about a registered MCP server"""
    name: str
    host: str
    port: int
    capabilities: List[str]
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_heartbeat: float = 0
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        self.last_heartbeat = time.time()


class ServiceRegistry:
    """Central registry for all MCP servers"""
    
    def __init__(self, heartbeat_interval: int = 30, health_check_interval: int = 10):
        self.services: Dict[str, ServiceInfo] = {}
        self.heartbeat_interval = heartbeat_interval
        self.health_check_interval = health_check_interval
        self._health_check_task = None
        
    async def register(self, service: ServiceInfo) -> bool:
        """Register a new MCP server"""
        try:
            self.services[service.name] = service
            logger.info(f"Registered service: {service.name} at {service.host}:{service.port}")
            
            # Start health monitoring if not already running
            if not self._health_check_task:
                self._health_check_task = asyncio.create_task(self._monitor_health())
                
            return True
        except Exception as e:
            logger.error(f"Failed to register service {service.name}: {e}")
            return False
    
    async def deregister(self, service_name: str) -> bool:
        """Remove a service from the registry"""
        if service_name in self.services:
            del self.services[service_name]
            logger.info(f"Deregistered service: {service_name}")
            return True
        return False
    
    async def update_heartbeat(self, service_name: str) -> bool:
        """Update the last heartbeat time for a service"""
        if service_name in self.services:
            self.services[service_name].last_heartbeat = time.time()
            self.services[service_name].status = ServiceStatus.HEALTHY
            return True
        return False
    
    def get_service(self, service_name: str) -> Optional[ServiceInfo]:
        """Get information about a specific service"""
        return self.services.get(service_name)
    
    def get_services_by_capability(self, capability: str) -> List[ServiceInfo]:
        """Find all services that have a specific capability"""
        return [
            service for service in self.services.values()
            if capability in service.capabilities and service.status == ServiceStatus.HEALTHY
        ]
    
    def get_healthy_services(self) -> List[ServiceInfo]:
        """Get all healthy services"""
        return [
            service for service in self.services.values()
            if service.status == ServiceStatus.HEALTHY
        ]
    
    async def _monitor_health(self):
        """Background task to monitor service health"""
        while True:
            try:
                current_time = time.time()
                for service_name, service in self.services.items():
                    time_since_heartbeat = current_time - service.last_heartbeat
                    
                    if time_since_heartbeat > self.heartbeat_interval * 2:
                        service.status = ServiceStatus.UNHEALTHY
                        logger.warning(f"Service {service_name} marked as unhealthy")
                    elif time_since_heartbeat > self.heartbeat_interval:
                        service.status = ServiceStatus.UNKNOWN
                        logger.warning(f"Service {service_name} heartbeat delayed")
                        
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    def to_dict(self) -> Dict:
        """Export registry state as dictionary"""
        return {
            name: asdict(service) for name, service in self.services.items()
        }
