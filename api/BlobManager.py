from .EnvManager import EnvManager
import json
from azure.storage.blob import BlobClient


class BlobManager:
    def upload_mentor_qa_pair(self, domain, question, answer):
        """Append a mentor Q&A pair to the mentorqa blob for the given domain."""
        blob = self.get_blob_client("mentorqa", domain)
        existing = ""
        if blob.exists():
            existing = blob.download_blob().readall().decode("utf-8")
        record = json.dumps({"question": question, "answer": answer}) + "\n"
        blob.upload_blob(existing + record, overwrite=True)
    def get_mentor_qa_pairs(self, domain):
        """Return JSON string of mentor Q&A pairs for a domain."""
        blob = self.get_blob_client("mentorqa", domain)
        if not blob.exists():
            return json.dumps([])
        data = blob.download_blob().readall().decode("utf-8").strip().splitlines()
        pairs = [json.loads(line) for line in data]
        return json.dumps(pairs)
    def __init__(self):
        env = EnvManager()
        self.storage_conn = env.get_required("AzureWebJobsStorage")
        self.PROFILES_BLOB = env.get_required("AGENTPROFILESBLOB")
        self.AGENTDIRS = self.load_json_from_blob("contexts", env.get_required("AGENTDIRECTIVESBLOB"))
        self.AGENTPROFILES = self.load_json_from_blob("contexts", self.PROFILES_BLOB)
        self.DOMAINKNOW = self.load_json_from_blob("knowledge", env.get_required("DOMAINKNOWLEDGEBLOB"))

    def load_json_from_blob(self, container, blob):
        bc = BlobClient.from_connection_string(self.storage_conn,
               container_name=container, blob_name=blob)
        return json.loads(bc.download_blob().readall())

    def get_blob_client(self, container, key):
        """Return blob client, constructing mentor Q&A blob name if needed."""
        if container == "mentorqa":
            blobname = f"{key}mentor_qa.jsonl"
        else:
            blobname = key
        return BlobClient.from_connection_string(self.storage_conn,
               container_name=container, blob_name=blobname)
