"""
LoRAPipeline class for automating Azure ML LoRA adapter training and registration.
"""

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

class LoRAPipeline:
    """
    LoRAPipeline automates the Azure ML workflow for LoRA adapter training and registration.
    """
    def __init__(self):
        """
        Authenticate and connect to Azure ML workspace using environment variables and DefaultAzureCredential.
        """
        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group  = os.environ["AZURE_RESOURCE_GROUP"]
        workspace_name  = os.environ["AZURE_WORKSPACE"]

        self.ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id,
            resource_group,
            workspace_name,
        )

    def provision_compute(self, compute_name="lora-cluster"):
        """
        Provision (or get) a spot-priced GPU cluster for training.
        Checks if the cluster exists; if not, creates a new one with spot pricing (low_priority).
        Returns:
            str: Name of the compute cluster
        """
        if compute_name not in [c.name for c in self.ml_client.compute.list()]:
            compute = AmlCompute(
                name=compute_name,
                size="STANDARD_NC6",
                min_instances=0,
                max_instances=4,
                idle_time_before_scale_down=300,
                tier="low_priority",  # spot pricing
            )
            self.ml_client.compute.begin_create_or_update(compute).result()
        else:
            compute = self.ml_client.compute.get(compute_name)
        return compute_name

    def setup_environment(self, env_name="lora-env"):
        """
        Create (or get) the Conda environment for training.
        Checks if the environment exists; if not, creates it from environment.yml.
        Returns:
            str: Name of the environment
        """
        if env_name not in [e.name for e in self.ml_client.environments.list()]:
            env = Environment(
                name=env_name,
                description="LoRA training env",
                conda_file="environment.yml",   # see snippet below
                build=BuildContext(path=".")     # assumes environment.yml is in cwd
            )
            self.ml_client.environments.create_or_update(env)
        else:
            env = self.ml_client.environments.get(env_name, version="1")
        return env_name

    def submit_training_job(self, compute_name, env_name):
        """
        Define and submit the CommandJob for multi-LoRA training.
        Specifies compute, environment, code location, and training command.
        Returns:
            CommandJob: The submitted job object
        """
        job = CommandJob(
            display_name="lora-multi-adapter-job",
            compute=compute_name,
            environment=env_name,
            code="./",          # your training script folder
            command=(
                "python train_lora.py "
                "--model meta-llama/Llama-3.1-8B-Instruct "
                "--data-path ./data/train.jsonl "
                "--output-dir ./outputs "
                "--adapters qv ko"
            ),
            outputs={
                "qv_adapter": Output(type="uri_folder", path="./outputs/lora_qv"),
                "ko_adapter": Output(type="uri_folder", path="./outputs/lora_ko"),
            },
            experiment_name="lora_experiments",
        )
        submitted_job = self.ml_client.jobs.create_or_update(job)
        return submitted_job

    def stream_job_logs(self, job_name):
        """
        Stream job logs to the console until training completes.
        Args:
            job_name (str): Name of the submitted job
        """
        self.ml_client.jobs.stream(job_name)

    def register_adapters(self, submitted_job):
        """
        Register each trained adapter as a Model in Azure ML.
        For each adapter (qv, ko), registers the output folder as a model asset.
        Args:
            submitted_job (CommandJob): The completed job object
        """
        for adapter in ["qv", "ko"]:
            adapter_path = f"{submitted_job.outputs[adapter + '_adapter'].uri}"
            model = Model(
                path=adapter_path,
                name=f"lora-{adapter}-adapter",
                type="custom_model",   # or transformer_adapter
                description=f"LoRA {adapter} adapter for Llama-3.1-8B",
            )
            self.ml_client.models.create_or_update(model)
            print(f"Registered model: lora-{adapter}-adapter")

    def run(self):
        """
        Main method to execute the full pipeline:
            1. Provision compute
            2. Set up environment
            3. Submit training job
            4. Stream logs
            5. Register adapters
        """
        compute_name = self.provision_compute()
        env_name = self.setup_environment()
        submitted_job = self.submit_training_job(compute_name, env_name)
        self.stream_job_logs(submitted_job.name)
        self.register_adapters(submitted_job)
        print("All done! Your LoRA adapters are trained and registered.")
