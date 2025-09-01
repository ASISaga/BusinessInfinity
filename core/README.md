# Core Functionality Modules

This directory contains the consolidated core functionality for BusinessInfinity, merging overlapping features from multiple teams.

## Module Structure

### `agents.py` - Unified Agent Management
- **Consolidates**: `api/AgentManager.py`, `app/agents.py`, `app/aml_chat.py`
- **Features**: 
  - Semantic Kernel agent orchestration
  - Azure ML endpoint integration
  - Agent profile management
  - ChromaDB knowledge integration

### `ml.py` - Azure ML Management  
- **Consolidates**: `app/aml.py`, `api/MLClientManager.py`
- **Features**:
  - AML endpoint inference
  - ML client management
  - Pipeline orchestration
  - Training job management

### `storage.py` - Unified Storage Management
- **Consolidates**: `app/storage.py`, `api/ConversationManager.py`, `api/TrainingDataManager.py`
- **Features**:
  - Azure Tables operations
  - Azure Blob Storage operations
  - Azure Queue operations
  - Conversation management
  - Training data management

### `environment.py` - Enhanced Environment Management
- **Enhances**: `api/EnvManager.py`
- **Features**:
  - Centralized environment variable access
  - Enhanced type conversion
  - Azure service configuration helpers
  - Configuration validation

## Usage

### Import Consolidated Modules
```python
from core.agents import agent_manager
from core.ml import ml_manager
from core.storage import storage_manager
from core.environment import env_manager
```

### Backwards Compatibility
Old imports still work with deprecation warnings:
```python
# Still works but shows deprecation warning
from api.AgentManager import AgentManager
from app.aml import aml_infer
```

## Benefits

1. **Eliminated Duplication**: Removed overlapping functionality across teams
2. **Unified API**: Consistent interface for similar operations
3. **Enhanced Features**: Combined best practices from all implementations
4. **Backwards Compatibility**: Existing code continues to work
5. **Better Testing**: Centralized functionality easier to test and maintain

## Migration Guide

### For New Code
Use the consolidated core modules:
```python
# New approach
from core.agents import agent_manager
response = await agent_manager.ask_agent("cmo", "Create marketing plan")
```

### For Existing Code
- Continue using existing imports (with warnings)
- Gradually migrate to core modules
- Use deprecation warnings as guidance for updates
