from .EnvManager import EnvManager
import json
from azure.storage.blob import BlobClient


class TrainingDataManager:
    """
    Manages interactions with Azure Blob Storage for mentor Q&A pairs and agent context/profile/knowledge blobs.
    """
    def upload_mentor_qa_pair(self, domain, question, answer):
        """
        Append a mentor Q&A pair to the mentorqa blob for the given domain.
        Each Q&A pair is stored as a JSON line in a .jsonl blob named <domain>mentor_qa.jsonl.
        If the blob exists, the new record is appended; otherwise, a new blob is created.
        Args:
            domain (str): The domain for which the Q&A is relevant.
            question (str): The mentor's question.
            answer (str): The mentor's answer.
        """
        blob = self.get_blob_client("mentorqa", domain)
        existing = ""
        if blob.exists():
            # Download existing blob content as UTF-8 string
            existing = blob.download_blob().readall().decode("utf-8")
        # Prepare new Q&A record as a JSON line
        record = json.dumps({"question": question, "answer": answer}) + "\n"
        # Upload the combined content, overwriting the blob
        blob.upload_blob(existing + record, overwrite=True)
    
    def get_mentor_qa_pairs(self, domain):
        """
        Retrieve all mentor Q&A pairs for a given domain from the mentorqa blob.
        Returns:
            str: JSON string of a list of Q&A pairs, each as a dict with 'question' and 'answer'.
        """
        blob = self.get_blob_client("mentorqa", domain)
        if not blob.exists():
            # If blob does not exist, return empty list
            return json.dumps([])
        # Download blob content, split into lines, and parse each line as JSON
        data = blob.download_blob().readall().decode("utf-8").strip().splitlines()
        pairs = [json.loads(line) for line in data]
        return json.dumps(pairs)
    
    def __init__(self):
        """
        Initialize BlobManager with environment variables and load agent context/profile/knowledge blobs.
        """
        env = EnvManager()
        # Azure Storage connection string
        self.storage_conn = env.get_required("AzureWebJobsStorage")
        # Blob names for agent profiles and directives
        self.PROFILES_BLOB = env.get_required("AGENTPROFILESBLOB")
        # Load agent directives, profiles, and domain knowledge from blobs
        self.AGENTDIRS = self.load_json_from_blob("contexts", env.get_required("AGENTDIRECTIVESBLOB"))
        self.AGENTPROFILES = self.load_json_from_blob("contexts", self.PROFILES_BLOB)
        self.DOMAINKNOW = self.load_json_from_blob("knowledge", env.get_required("DOMAINKNOWLEDGEBLOB"))

    def load_json_from_blob(self, container, blob):
        """
        Load and parse JSON content from a blob in the specified container.
        Args:
            container (str): The container name.
            blob (str): The blob name.
        Returns:
            dict or list: Parsed JSON content from the blob.
        """
        bc = BlobClient.from_connection_string(
            self.storage_conn,
            container_name=container,
            blob_name=blob
        )
        return json.loads(bc.download_blob().readall())

    def get_blob_client(self, container, key):
        """
        Return a BlobClient for the specified container and key.
        For mentor Q&A blobs, constructs the blob name as <domain>mentor_qa.jsonl.
        Args:
            container (str): The container name.
            key (str): The domain or blob key.
        Returns:
            BlobClient: The blob client for the specified blob.
        """
        if container == "mentorqa":
            blobname = f"{key}mentor_qa.jsonl"
        else:
            blobname = key
        return BlobClient.from_connection_string(
            self.storage_conn,
            container_name=container,
            blob_name=blobname
        )
