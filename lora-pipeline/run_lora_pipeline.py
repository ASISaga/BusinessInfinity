
# run_lora_pipeline.py
# This script automates the end-to-end process of training and registering LoRA adapters using Azure ML.
# Steps:
#   1. Authenticate and connect to Azure ML workspace
#   2. Provision (or get) a spot-priced GPU cluster
#   3. Create (or get) the Conda environment for training
#   4. Define and submit a CommandJob for multi-LoRA training
#   5. Wait for job completion
#   6. Register each trained adapter as a Model in Azure ML


import os
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    AmlCompute,
    Environment,
    CommandJob,
    Model,
    Output,
    BuildContext,
)

from LoRAPipeline import LoRAPipeline

if __name__ == "__main__":
    # Example usage: initialize and run the pipeline
    pipeline = LoRAPipeline()
    pipeline.run()


# 1. Authenticate and connect to Azure ML workspace
#    - Uses environment variables for subscription, resource group, and workspace name
#    - Uses DefaultAzureCredential for authentication (supports managed identity, CLI, etc.)
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
resource_group  = os.environ["AZURE_RESOURCE_GROUP"]
workspace_name  = os.environ["AZURE_WORKSPACE"]

ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id,
    resource_group,
    workspace_name,
)


# 2. Provision (or get) a spot-priced GPU cluster for training
#    - Checks if the cluster exists; if not, creates a new one with spot pricing (low_priority)
#    - Uses STANDARD_NC6 GPU VM size, scales between 0 and 4 instances
compute_name = "lora-cluster"
if compute_name not in [c.name for c in ml_client.compute.list()]:
    compute = AmlCompute(
        name=compute_name,
        size="STANDARD_NC6",
        min_instances=0,
        max_instances=4,
        idle_time_before_scale_down=300,
        tier="low_priority",  # spot pricing
    )
    ml_client.compute.begin_create_or_update(compute).result()
else:
    compute = ml_client.compute.get(compute_name)


# 3. Create (or get) the Conda environment for training
#    - Checks if the environment exists; if not, creates it from environment.yml
#    - environment.yml should specify all required Python packages for LoRA training
env_name = "lora-env"
if env_name not in [e.name for e in ml_client.environments.list()]:
    env = Environment(
        name=env_name,
        description="LoRA training env",
        conda_file="environment.yml",   # see snippet below
        build=BuildContext(path=".")     # assumes environment.yml is in cwd
    )
    ml_client.environments.create_or_update(env)
else:
    env = ml_client.environments.get(env_name, version="1")

# Example environment.yml (must be present in the same folder):
# name: lora-env
# dependencies:
#   - python=3.10
#   - pip:
#     - torch~=2.0
#     - transformers~=4.35
#     - accelerate~=0.20
#     - peft~=0.4
#     - datasets
#     - azure-ai-ml



# 4. Directly invoke LoRATrainer for multi-LoRA training

from LoRATrainer import LoRATrainer
from peft import TaskType


# Load training parameters from external file
training_params_path = "./config/lora_training_params.json"
with open(training_params_path, "r") as f:
    training_params = json.load(f)
model_name = training_params["model_name"]
data_path = training_params["data_path"]
output_dir = training_params["output_dir"]




# Load adapters configuration from new external file
import json
lora_adapters_path = "./config/lora_adapters.json"
with open(lora_adapters_path, "r") as f:
    adapters = json.load(f)

# Convert string task_type to TaskType enum
for adapter in adapters:
    if "task_type" in adapter and isinstance(adapter["task_type"], str):
        if adapter["task_type"].lower() == "causal_lm":
            adapter["task_type"] = TaskType.CAUSAL_LM

# Train adapters using LoRATrainer
trainer = LoRATrainer(
    model_name=model_name,
    data_path=data_path,
    output_dir=output_dir,
    adapters=adapters
)
trainer.train()

# 5. Register each trained adapter as a Model in Azure ML
for adapter_cfg in adapters:
    adapter = adapter_cfg["adapter_name"]
    adapter_path = f"{output_dir}/{adapter}"
    model = Model(
        path=adapter_path,
        name=f"lora-{adapter}-adapter",
        type="custom_model",   # or transformer_adapter
        description=f"LoRA {adapter} adapter for Llama-3.1-8B",
    )
    ml_client.models.create_or_update(model)
    print(f"Registered model: lora-{adapter}-adapter")

print("All done! Your LoRA adapters are trained and registered.")