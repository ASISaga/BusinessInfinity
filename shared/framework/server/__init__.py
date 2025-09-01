"""
Framework Server package - provides server-side framework components
"""

# Import server components with error handling for missing dependencies
__all__ = []

# Note: Some components may require Azure Service Bus or other dependencies
# that might not be available in all environments

try:
    from . import decision_engine
    __all__.append('decision_engine')
except ImportError:
    pass

try:
    from . import azure_ml
    __all__.append('azure_ml')
except ImportError:
    pass

try:
    from . import adapters
    __all__.append('adapters')
except ImportError:
    pass

# Note: governance and service_bus depend on azure.servicebus which may not be installed
try:
    from . import governance
    __all__.append('governance')
except ImportError:
    pass

try:
    from . import service_bus
    __all__.append('service_bus')
except ImportError:
    pass