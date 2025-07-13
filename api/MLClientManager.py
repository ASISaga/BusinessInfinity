from .EnvManager import EnvManager
import json
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

class MLClientManager:
    def get_input_path(self, domain):
        """Return AML datastore input path for mentor Q&A for the given domain."""
        return f"azureml://datastores/workspaceblob/paths/mentorqa/{domain}mentor_qa.jsonl"
    def __init__(self):
        env = EnvManager()
        self.subscription_id = env.get_required("AZURESUBSCRIPTION_ID")
        self.resource_group_name = env.get_required("AZURERESOURCEGROUP")
        self.workspace_name = env.get_required("AZUREML_WORKSPACE")
        self.pipeline_name = env.get_required("PIPELINEENDPOINT_NAME")
        self._client = None

    def get_client(self):
        if self._client is None:
            self._client = MLClient(
                DefaultAzureCredential(),
                subscription_id=self.subscription_id,
                resource_group_name=self.resource_group_name,
                workspace_name=self.workspace_name
            )
        return self._client

    @property
    def PIPELINE_NAME(self):
        return self.pipeline_name

    def invoke_pipeline(self, domain):
        client = self.get_client()
        inputpath = self.get_input_path(domain)
        result = client.pipelineendpoints.invoke(
            name=self.PIPELINE_NAME,
            inputs={"qajsonl": inputpath}
        )
        return json.dumps({"pipelinejobid": result.id})
