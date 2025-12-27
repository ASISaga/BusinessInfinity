"""
Generic Storage Abstractions for Runtime

Provides generic storage interfaces and implementations that can be used
by any application. These delegate to AgentOperatingSystem when available.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime


class IStorageProvider(ABC):
    """
    Generic storage provider interface.
    
    Applications should use this interface instead of directly using
    Azure Blob Storage, Cosmos DB, etc.
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get a value by key."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value with optional TTL (time-to-live in seconds)."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a value by key."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        pass
    
    @abstractmethod
    async def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List all keys, optionally filtered by prefix."""
        pass


class MemoryStorageProvider(IStorageProvider):
    """
    In-memory storage provider for development/testing.
    
    Note: Data is lost when the application restarts.
    """
    
    def __init__(self):
        self._store: Dict[str, Any] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        self._store[key] = value
        # Note: TTL not implemented in memory provider
        return True
    
    async def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        return key in self._store
    
    async def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        if prefix:
            return [k for k in self._store.keys() if k.startswith(prefix)]
        return list(self._store.keys())


class AOSStorageProvider(IStorageProvider):
    """
    Storage provider that delegates to AgentOperatingSystem.
    
    This wraps AOS storage services to provide a consistent interface.
    """
    
    def __init__(self, aos_storage_manager=None):
        """
        Initialize with AOS storage manager.
        
        Args:
            aos_storage_manager: AgentOperatingSystem storage manager instance
        """
        if aos_storage_manager is None:
            # Try to import and create AOS storage manager
            try:
                from AgentOperatingSystem.storage.manager import UnifiedStorageManager
                self.storage_manager = UnifiedStorageManager()
            except ImportError:
                raise RuntimeError(
                    "AgentOperatingSystem is not installed. "
                    "Install with: pip install AgentOperatingSystem"
                )
        else:
            self.storage_manager = aos_storage_manager
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from AOS storage."""
        try:
            return await self.storage_manager.get(key)
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in AOS storage."""
        try:
            await self.storage_manager.set(key, value, ttl=ttl)
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from AOS storage."""
        try:
            await self.storage_manager.delete(key)
            return True
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in AOS storage."""
        try:
            return await self.storage_manager.exists(key)
        except Exception:
            return False
    
    async def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List keys from AOS storage."""
        try:
            return await self.storage_manager.list_keys(prefix=prefix)
        except Exception:
            return []


def create_storage_provider(
    provider_type: str = "memory",
    **kwargs
) -> IStorageProvider:
    """
    Factory function to create storage provider.
    
    Args:
        provider_type: Type of storage ("memory", "aos")
        **kwargs: Additional arguments for the provider
        
    Returns:
        Storage provider instance
    """
    if provider_type == "memory":
        return MemoryStorageProvider()
    elif provider_type == "aos":
        return AOSStorageProvider(kwargs.get('aos_storage_manager'))
    else:
        raise ValueError(f"Unknown storage provider type: {provider_type}")
