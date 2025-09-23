"""
ML Pipeline integration for BusinessInfinity
This module exposes ML features by importing from RealmOfAgents.AgentOperatingSystem.

To use ML features in BusinessInfinity, import from core.features.ml:

from core.features.ml import MLPipelineManager, trigger_lora_training, run_azure_ml_pipeline, aml_infer

These are wrappers for the AOS ML pipeline. See RealmOfAgents/AgentOperatingSystem for implementation details.

Example usage:
  manager = MLPipelineManager()
  await manager.train_adapter(agent_role, training_params, adapter_config)
  await manager.infer(agent_role, prompt)
  await run_azure_ml_pipeline(subscription_id, resource_group, workspace_name)
  await aml_infer(agent_id, prompt)
"""

# Import the AOS ML pipeline manager and operations
from RealmOfAgents.AgentOperatingSystem.MLPipelineManager import MLPipelineManager
from RealmOfAgents.AgentOperatingSystem.ml_pipeline_ops import trigger_lora_training, run_azure_ml_pipeline, aml_infer


# Import UnifiedEnvManager from AOS
from RealmOfAgents.AgentOperatingSystem.environment import UnifiedEnvManager

# Example usage in BusinessInfinity:
# manager = MLPipelineManager()
# await manager.train_adapter(agent_role, training_params, adapter_config)
# await manager.infer(agent_role, prompt)
# await run_azure_ml_pipeline(subscription_id, resource_group, workspace_name)
# await aml_infer(agent_id, prompt)
