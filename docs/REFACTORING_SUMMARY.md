# BusinessInfinity - Refactored Architecture

This repository has been completely refactored into a feature-based architecture for better organization and maintainability.

## New Structure

### Features (Business Functionality)
- **`features/authentication/`** - Authentication and authorization
- **`features/agents/`** - AI agent management and interactions  
- **`features/storage/`** - Data storage and conversation management
- **`features/ml_pipeline/`** - Machine learning and training pipelines
- **`features/environment/`** - Configuration and environment management
- **`features/api/`** - API routing and business orchestration
- **`features/azure_functions/`** - Azure Functions integration

### Shared (Common Code)
- **`shared/models/`** - Common data models
- **`shared/utils/`** - Shared utilities and helpers
- **`shared/framework/`** - Framework components (MCP, adapters, etc.)

## Key Changes

### Consolidation Completed
- ✅ Removed overlapping functionality across directories
- ✅ Deleted deprecated wrapper modules that only imported from unified managers
- ✅ Removed entire `core/` directory after moving all functionality
- ✅ Removed `v1_backup/` directory (deprecated V1 code)
- ✅ Consolidated similar manager classes into unified feature managers

### Import Structure
All features expose their main functionality through clean imports:

```python
from features.storage import storage_manager
from features.agents import agent_manager  
from features.ml_pipeline import ml_manager
from features.environment import env_manager
from features.authentication import validate_jwt
from features.api import Router, Orchestrator
```

### Backward Compatibility
- **Not maintained** as per requirements - deprecated code has been deleted
- Old `core.*` imports will fail and need to be updated to `features.*`

## Usage

The main entry point remains `function_app.py` which now imports from the new feature structure.

Each feature is self-contained with its own manager and dependencies, making the codebase more modular and maintainable.