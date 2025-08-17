"""
MCP Hub Main Application
Optimized for Railway deployment with 32 vCPU and 32GB RAM
"""

import asyncio
import uvloop
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from typing import Dict, Any

from src.config import get_config, HubConfig
from src.registry import ServiceRegistry, ServiceInfo, ServiceStatus
from src.router import Router, RouteRequest, RouteResponse

# Set up optimized event loop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Global instances
registry: ServiceRegistry = None
router: Router = None
config: HubConfig = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global registry, router, config
    
    # Initialize configuration
    config = get_config()
    logger.info(f"Starting MCP Hub with {config.performance.worker_processes} workers")
    logger.info(f"Memory per worker: {config.performance.max_memory_per_worker}MB")
    
    # Initialize registry and router
    registry = ServiceRegistry(
        heartbeat_interval=config.heartbeat_interval,
        health_check_interval=config.health_check_interval
    )
    router = Router(registry, config.load_balancer_strategy)
    
    # Start background tasks
    logger.info("MCP Hub initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down MCP Hub")


# Create FastAPI app
app = FastAPI(
    title="MCP Hub",
    description="Central orchestrator for MCP servers - Optimized for Railway",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "services": len(registry.services) if registry else 0,
        "config": {
            "workers": config.performance.worker_processes if config else 0,
            "memory_per_worker": config.performance.max_memory_per_worker if config else 0,
        }
    }


@app.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    if not config.enable_metrics:
        raise HTTPException(status_code=403, detail="Metrics disabled")
    
    return {
        "registry": registry.to_dict() if registry else {},
        "router": router.get_routing_stats() if router else {},
        "config": config.to_dict() if config else {}
    }


@app.post("/register")
async def register_service(service_data: Dict[str, Any]):
    """Register a new MCP service"""
    try:
        service = ServiceInfo(
            name=service_data["name"],
            host=service_data["host"],
            port=service_data["port"],
            capabilities=service_data.get("capabilities", []),
            metadata=service_data.get("metadata", {})
        )
        
        success = await registry.register(service)
        if success:
            return {"status": "registered", "service": service.name}
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
            
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required field: {e}")
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deregister/{service_name}")
async def deregister_service(service_name: str):
    """Deregister a service"""
    success = await registry.deregister(service_name)
    if success:
        return {"status": "deregistered", "service": service_name}
    else:
        raise HTTPException(status_code=404, detail="Service not found")


@app.post("/heartbeat/{service_name}")
async def heartbeat(service_name: str):
    """Update service heartbeat"""
    success = await registry.update_heartbeat(service_name)
    if success:
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=404, detail="Service not found")


@app.post("/route")
async def route_request(request_data: Dict[str, Any]):
    """Route a request to appropriate MCP server"""
    try:
        request = RouteRequest(
            method=request_data["method"],
            params=request_data.get("params", {}),
            capability=request_data.get("capability"),
            target_service=request_data.get("target_service"),
            request_id=request_data.get("request_id")
        )
        
        response = await router.route(request)
        
        if response.success:
            return {
                "success": True,
                "data": response.data,
                "service": response.service_name,
                "request_id": response.request_id
            }
        else:
            raise HTTPException(status_code=503, detail=response.error)
            
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required field: {e}")
    except Exception as e:
        logger.error(f"Routing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/services")
async def list_services():
    """List all registered services"""
    return {
        "services": registry.to_dict() if registry else {},
        "healthy_count": len(registry.get_healthy_services()) if registry else 0
    }


@app.get("/services/{capability}")
async def get_services_by_capability(capability: str):
    """Get services that support a specific capability"""
    services = registry.get_services_by_capability(capability) if registry else []
    return {
        "capability": capability,
        "services": [{"name": s.name, "host": s.host, "port": s.port} for s in services]
    }


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration
    config = get_config()
    
    # Run with optimized settings for Railway
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        workers=1,  # Gunicorn will handle multiple workers
        loop="uvloop",
        access_log=True,
        log_level=config.log_level.lower()
    )
