from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import AmlCompute, Environment, BuildContext

from LoRAPipeline import LoRAPipeline
from LoRATrainer import LoRATrainer
from peft import TaskType

class MLManager:
    """
    MLManager handles Azure ML workspace authentication, compute/environment provisioning,
    LoRA pipeline execution, adapter training, registration, and lifecycle management.
    """
    def __init__(self, subscription_id, resource_group, workspace_name):
        """
        Initialize MLManager with Azure ML workspace details and authenticate client.
        Args:
            subscription_id (str): Azure subscription ID
            resource_group (str): Azure resource group name
            workspace_name (str): Azure ML workspace name
        """
        self.ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id,
            resource_group,
            workspace_name,
        )

    def run_pipeline(self):
        """
        Run the LoRA pipeline using the LoRAPipeline class.
        This is a placeholder for any pipeline-wide orchestration logic.
        """
        pipeline = LoRAPipeline()
        pipeline.run()

    def train_adapters(self, training_params, adapters):
        """
        Train LoRA adapters using LoRATrainer and register them in Azure ML.
        Args:
            training_params (dict): Training parameters loaded from config file
            adapters (list): List of adapter configs loaded from config file
        Returns:
            adapters (list): List of trained adapter configs
        """
        model_name = training_params["model_name"]
        data_path = training_params["data_path"]
        output_dir = training_params["output_dir"]

        # Convert string task_type to TaskType enum for each adapter
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
        # Register trained adapters as models in Azure ML
        self.register_adapters(adapters, output_dir)
        return adapters

    def start_adapter(self, adapter_name):
        """
        Start a LoRA adapter (stub).
        Args:
            adapter_name (str): Name of the adapter to start
        """
        print(f"Starting adapter: {adapter_name}")
        # Add actual start logic here (e.g., load into inference server, enable endpoint, etc.)

    def stop_adapter(self, adapter_name):
        """
        Stop a LoRA adapter (stub).
        Args:
            adapter_name (str): Name of the adapter to stop
        """
        print(f"Stopping adapter: {adapter_name}")
        # Add actual stop logic here (e.g., unload from server, disable endpoint, etc.)

    def get_or_create_compute(self, compute_name="lora-cluster", vm_size="STANDARD_NC6", min_instances=0, max_instances=4, idle_time=300, tier="low_priority"):
        """
        Get or create a GPU compute cluster for training in Azure ML.
        Args:
            compute_name (str): Name of the compute cluster
            vm_size (str): VM size for the cluster
            min_instances (int): Minimum number of nodes
            max_instances (int): Maximum number of nodes
            idle_time (int): Idle time before scale down (seconds)
            tier (str): Pricing tier (e.g., 'low_priority' for spot)
        Returns:
            compute (AmlCompute): The compute resource object
        """
        if compute_name not in [c.name for c in self.ml_client.compute.list()]:
            compute = AmlCompute(
                name=compute_name,
                size=vm_size,
                min_instances=min_instances,
                max_instances=max_instances,
                idle_time_before_scale_down=idle_time,
                tier=tier,
            )
            self.ml_client.compute.begin_create_or_update(compute).result()
        else:
            compute = self.ml_client.compute.get(compute_name)
        return compute

    def get_or_create_environment(self, env_name="lora-env", conda_file="environment.yml", description="LoRA training env", build_path="."):
        """
        Get or create a Conda environment for training in Azure ML.
        Args:
            env_name (str): Name of the environment
            conda_file (str): Path to environment.yml file
            description (str): Description of the environment
            build_path (str): Build context path
        Returns:
            env (Environment): The environment resource object
        """
        if env_name not in [e.name for e in self.ml_client.environments.list()]:
            env = Environment(
                name=env_name,
                description=description,
                conda_file=conda_file,
                build=BuildContext(path=build_path)
            )
            self.ml_client.environments.create_or_update(env)
        else:
            env = self.ml_client.environments.get(env_name, version="1")
        return env

    def register_adapters(self, adapters, output_dir, base_model_desc="Llama-3.1-8B"):
        """
        Register trained LoRA adapters as models in Azure ML workspace.
        Args:
            adapters (list): List of adapter configs
            output_dir (str): Directory containing trained adapter files
            base_model_desc (str): Description of the base model
        """
        from azure.ai.ml.entities import Model
        for adapter_cfg in adapters:
            adapter = adapter_cfg["adapter_name"]
            adapter_path = f"{output_dir}/{adapter}"
            model = Model(
                path=adapter_path,
                name=f"lora-{adapter}-adapter",
                type="custom_model",   # or transformer_adapter
                description=f"LoRA {adapter} adapter for {base_model_desc}",
            )
            self.ml_client.models.create_or_update(model)
            print(f"Registered model: lora-{adapter}-adapter")
