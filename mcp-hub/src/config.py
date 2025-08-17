"""
Configuration management for MCP Hub
Optimized for Railway deployment with 32 vCPU and 32GB RAM
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import multiprocessing

# Detect available resources
CPU_COUNT = multiprocessing.cpu_count()
MEMORY_GB = 32  # Railway allocation

@dataclass
class PerformanceConfig:
    """Performance tuning configuration"""
    # Worker configuration (optimized for 32 cores)
    worker_processes: int = min(16, CPU_COUNT)  # Leave headroom for OS
    worker_threads: int = 4
    max_connections_per_worker: int = 2000
    
    # Connection pooling
    connection_pool_size: int = 100
    connection_timeout: int = 30
    
    # Request handling
    request_timeout: int = 120
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    
    # Memory optimization
    max_memory_per_worker: int = 1536  # MB (24GB total for 16 workers)
    gc_threshold: int = 1000
    
    # Async optimization
    event_loop_policy: str = "uvloop"
    async_pool_size: int = 1000


@dataclass
class ServiceConfig:
    """Configuration for individual MCP services"""
    name: str
    enabled: bool = True
    max_instances: int = 3
    memory_limit: int = 512  # MB
    cpu_shares: int = 1024
    health_check_interval: int = 30
    timeout: int = 60
    retry_attempts: int = 3
    retry_delay: int = 5


@dataclass
class HubConfig:
    """Main configuration for MCP Hub"""
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Railway-specific
    railway_environment: str = field(default_factory=lambda: os.getenv("RAILWAY_ENVIRONMENT", "production"))
    railway_static_url: str = field(default_factory=lambda: os.getenv("RAILWAY_STATIC_URL", ""))
    
    # Performance settings
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Service registry settings
    heartbeat_interval: int = 30
    health_check_interval: int = 10
    service_timeout: int = 300
    
    # Load balancing
    load_balancer_strategy: str = "least_connections"  # Best for high concurrency
    sticky_sessions: bool = False
    session_timeout: int = 3600
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    log_level: str = "INFO"
    
    # Security
    enable_auth: bool = True
    auth_token_expiry: int = 3600
    max_failed_auth_attempts: int = 5
    
    # Service configurations
    services: Dict[str, ServiceConfig] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls) -> "HubConfig":
        """Create configuration from environment variables"""
        config = cls()
        
        # Override with environment variables
        config.host = os.getenv("MCP_HUB_HOST", config.host)
        config.port = int(os.getenv("MCP_HUB_PORT", str(config.port)))
        config.debug = os.getenv("MCP_HUB_DEBUG", "false").lower() == "true"
        
        # Performance tuning for Railway
        if os.getenv("RAILWAY_ENVIRONMENT"):
            # Optimize for Railway's infrastructure
            config.performance.worker_processes = 16
            config.performance.max_connections_per_worker = 2000
            config.performance.connection_pool_size = 200
            config.performance.async_pool_size = 2000
            
        return config
    
    @classmethod
    def from_file(cls, path: str) -> "HubConfig":
        """Load configuration from JSON file"""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "railway_environment": self.railway_environment,
            "performance": {
                "worker_processes": self.performance.worker_processes,
                "worker_threads": self.performance.worker_threads,
                "max_connections_per_worker": self.performance.max_connections_per_worker,
                "connection_pool_size": self.performance.connection_pool_size,
                "max_memory_per_worker": self.performance.max_memory_per_worker,
            },
            "load_balancer_strategy": self.load_balancer_strategy,
            "services": {
                name: {
                    "enabled": svc.enabled,
                    "max_instances": svc.max_instances,
                    "memory_limit": svc.memory_limit,
                } for name, svc in self.services.items()
            }
        }


# Global configuration instance
_config: Optional[HubConfig] = None


def get_config() -> HubConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = HubConfig.from_env()
    return _config


def set_config(config: HubConfig):
    """Set the global configuration instance"""
    global _config
    _config = config
