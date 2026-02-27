"""
Generic Route Registry System

Provides a generic system for registering and managing routes in Azure Functions
or other HTTP frameworks. This can be used by any application built on the runtime.
"""

import logging
from typing import Dict, Any, Optional, Callable, List, Awaitable
from dataclasses import dataclass, field
from enum import Enum


class HttpMethod(Enum):
    """HTTP methods supported by the runtime."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthLevel(Enum):
    """Authentication levels for routes."""
    ANONYMOUS = "ANONYMOUS"
    FUNCTION = "FUNCTION"
    ADMIN = "ADMIN"


# Type alias for route handlers
# Handler receives a request object and returns a response
RouteHandler = Callable[[Any], Awaitable[Any]]


@dataclass
class Route:
    """
    Route definition for HTTP endpoints.
    
    This is a framework-agnostic route definition that can be adapted
    to Azure Functions, FastAPI, Flask, or other frameworks.
    """
    path: str
    handler: RouteHandler
    methods: List[HttpMethod] = field(default_factory=lambda: [HttpMethod.GET])
    auth_level: AuthLevel = AuthLevel.FUNCTION
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Framework-specific metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        methods_str = ", ".join(m.value for m in self.methods)
        return f"Route({self.path} [{methods_str}] - {self.description or 'No description'})"


class RouteRegistry:
    """
    Generic route registry for managing HTTP endpoints.
    
    This registry is framework-agnostic and can be adapted to:
    - Azure Functions
    - FastAPI
    - Flask
    - Django
    - Any other HTTP framework
    
    Applications register routes here, and the runtime adapts them
    to the target framework.
    """
    
    def __init__(self):
        self.routes: Dict[str, Route] = {}
        self.logger = logging.getLogger(__name__)
    
    def register(
        self,
        path: str,
        handler: RouteHandler,
        methods: Optional[List[HttpMethod]] = None,
        auth_level: AuthLevel = AuthLevel.FUNCTION,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **metadata
    ) -> Route:
        """
        Register a new route.
        
        Args:
            path: Route path (e.g., "/health", "/api/agents/{id}")
            handler: Async function to handle requests
            methods: List of HTTP methods (default: [GET])
            auth_level: Authentication level required
            description: Human-readable description
            tags: Tags for grouping/filtering routes
            **metadata: Framework-specific metadata
            
        Returns:
            The registered Route object
        """
        if methods is None:
            methods = [HttpMethod.GET]
        
        if tags is None:
            tags = []
        
        route = Route(
            path=path,
            handler=handler,
            methods=methods,
            auth_level=auth_level,
            description=description,
            tags=tags,
            metadata=metadata
        )
        
        self.routes[path] = route
        self.logger.info(f"Registered route: {route}")
        return route
    
    def get_route(self, path: str) -> Optional[Route]:
        """Get a route by path."""
        return self.routes.get(path)
    
    def get_routes_by_tag(self, tag: str) -> List[Route]:
        """Get all routes with a specific tag."""
        return [r for r in self.routes.values() if tag in r.tags]
    
    def get_all_routes(self) -> List[Route]:
        """Get all registered routes."""
        return list(self.routes.values())
    
    def unregister(self, path: str) -> bool:
        """
        Unregister a route.
        
        Args:
            path: Path of the route to unregister
            
        Returns:
            True if route was found and removed, False otherwise
        """
        if path in self.routes:
            del self.routes[path]
            self.logger.info(f"Unregistered route: {path}")
            return True
        return False
    
    def clear(self):
        """Clear all registered routes."""
        self.routes.clear()
        self.logger.info("Cleared all routes")


# Decorators for easy route registration

def route(
    registry: RouteRegistry,
    path: str,
    methods: Optional[List[HttpMethod]] = None,
    auth_level: AuthLevel = AuthLevel.FUNCTION,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    **metadata
):
    """
    Decorator for registering routes.
    
    Example:
        registry = RouteRegistry()
        
        @route(registry, "/health", methods=[HttpMethod.GET], auth_level=AuthLevel.ANONYMOUS)
        async def health_check(req):
            return {"status": "healthy"}
    """
    def decorator(func: RouteHandler):
        registry.register(
            path=path,
            handler=func,
            methods=methods,
            auth_level=auth_level,
            description=description,
            tags=tags,
            **metadata
        )
        return func
    return decorator
