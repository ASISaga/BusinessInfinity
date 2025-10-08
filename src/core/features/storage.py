"""
Consolidated Storage Management
Merges functionality from /storage/manager.py
"""

import os
import json
import time
import datetime
from typing import Dict, Any, List, Optional

try:
    from azure.data.tables import TableClient, TableServiceClient, TableEntity
    from azure.storage.queue import QueueClient
    from azure.storage.blob import BlobClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from AgentOperatingSystem.environment import EnvironmentManager, env_manager


class UnifiedStorageManager:
    """
    Business Infinity Storage Manager - extends AOS storage with business-specific operations:
    - Boardroom decision storage
    - Business metrics and KPI storage
    - Agent collaboration history
    - Business workflow state management
    """

    def __init__(self, env=None):
        # Initialize AOS storage manager with business-specific configuration
        super().__init__(env)
        
        # Business-specific storage configuration
        env_manager_instance = env or env_manager
        # For backward compatibility, allow passing an EnvironmentManager instance
        if isinstance(env_manager_instance, EnvironmentManager):
            env_manager = env_manager_instance
        else:
            env_manager = env_manager
        self.boardroom_table = env_manager.get("BOARDROOM_TABLE_NAME", "BoardroomDecisions")
        self.metrics_table = env_manager.get("METRICS_TABLE_NAME", "BusinessMetrics")
        self.collaboration_table = env_manager.get("COLLABORATION_TABLE_NAME", "AgentCollaboration")
        
    async def store_boardroom_decision(self, decision_data: Dict[str, Any]) -> bool:
        """Store boardroom decision with audit trail"""
        try:
            decision_data["timestamp"] = datetime.now().isoformat()
            decision_data["source"] = "business_infinity_boardroom"
            return await self.store_entity(self.boardroom_table, decision_data)
        except Exception as e:
            self.logger.error(f"Failed to store boardroom decision: {e}")
            return False
            
    async def store_business_metrics(self, metrics: Dict[str, Any], agent_id: str) -> bool:
        """Store business metrics for an agent"""
        try:
            metrics_data = {
                "agent_id": agent_id,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat(),
                "source": "business_infinity"
            }
            return await self.store_entity(self.metrics_table, metrics_data)
        except Exception as e:
            self.logger.error(f"Failed to store business metrics: {e}")
            return False
            
    async def get_boardroom_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent boardroom decisions"""
        try:
            return await self.get_entities(self.boardroom_table, limit=limit)
        except Exception as e:
            self.logger.error(f"Failed to get boardroom history: {e}")
            return []

        # Load agent data
        self.agent_dirs = None
        self.agent_profiles = None
        self.domain_knowledge = None
        self._load_agent_data()

    def _load_agent_data(self):
        """Load agent data from blobs"""
        try:
            if self.directives_blob:
                self.agent_dirs = self.load_json_from_blob("contexts", self.directives_blob)
            if self.profiles_blob:
                self.agent_profiles = self.load_json_from_blob("contexts", self.profiles_blob)
            if self.knowledge_blob:
                self.domain_knowledge = self.load_json_from_blob("knowledge", self.knowledge_blob)
        except Exception as e:
            print(f"Warning: Could not load agent data: {e}")

    # === Azure Tables Operations ===

    def get_table_client(self):
        """Get Azure Tables client (singleton pattern)"""
        if not AZURE_AVAILABLE:
            raise ImportError("Azure libraries are required for storage operations")
            
        if not self.table_conn:
            raise EnvironmentError("No table connection string configured")
            
        if self._table_client is None:
            self._table_client = TableClient.from_connection_string(
                self.table_conn, table_name=self.table_name
            )
        return self._table_client

    def get_cosmos_table_client(self):
        """Get Cosmos DB table client (singleton pattern)"""
        if not AZURE_AVAILABLE:
            raise ImportError("Azure libraries are required for storage operations")
            
        if not self.cosmos_endpoint or not self.cosmos_key:
            return None
        
        if self._service_client is None:
            self._service_client = TableServiceClient(
                endpoint=self.cosmos_endpoint, 
                credential=self.cosmos_key
            )
        if self._cosmos_table_client is None:
            self._cosmos_table_client = self._service_client.get_table_client(
                table_name=self.cosmos_container
            )
        return self._cosmos_table_client

    def to_row(self, boardroom_id: str, conversation_id: str, env: Dict[str, Any]) -> Dict[str, Any]:
        """Convert message envelope to table row"""
        pk = f"{boardroom_id}|{conversation_id}"
        rk = f"{int(time.time()*1000):013d}-{env['messageId']}"
        return {
            "PartitionKey": pk,
            "RowKey": rk,
            "Envelope": json.dumps(env)
        }

    def from_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Convert table row to message envelope"""
        return json.loads(row["Envelope"])

    def query_messages(self, boardroom_id: str, conversation_id: str, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query messages from table storage"""
        with self.get_table_client() as t:
            pk = f"{boardroom_id}|{conversation_id}"
            if since:
                flt = f"PartitionKey eq '{pk}' and RowKey gt '{since}'"
            else:
                flt = f"PartitionKey eq '{pk}'"
            return [self.from_row(e) for e in t.query_entities(flt, results_per_page=100)]

    # === Conversation Management ===

    def create_conversation(self, conv_id: str, domain: str):
        """Create a new conversation"""
        if not AZURE_AVAILABLE:
            raise ImportError("Azure libraries are required for storage operations")
            
        table = self.get_cosmos_table_client() or self.get_table_client()

        entity = TableEntity()
        entity["PartitionKey"] = conv_id
        entity["RowKey"] = conv_id
        entity["domain"] = domain
        entity["createdAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        entity["messages"] = json.dumps([])
        
        table.create_entity(entity=entity)

    def get_conversation(self, conv_id: str) -> Optional[str]:
        """Get conversation by ID"""
        table = self.get_cosmos_table_client() or self.get_table_client()
        try:
            entity = table.get_entity(partition_key=conv_id, row_key=conv_id)
            entity["messages"] = json.loads(entity.get("messages", "[]"))
            return json.dumps(entity)
        except Exception:
            return None

    def upsert_conversation(self, conv: Dict[str, Any], domain: str = None, answer_json: str = None):
        """Update conversation with new message"""
        if domain is not None and answer_json is not None:
            answer_obj = json.loads(answer_json)
            agent_msg = {
                "sender": domain,
                "text": answer_obj["answer"],
                "time": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            messages = conv.get("messages", [])
            if isinstance(messages, str):
                messages = json.loads(messages)
            messages.append(agent_msg)
            conv["messages"] = json.dumps(messages)
        
        table = self.get_cosmos_table_client() or self.get_table_client()
        table.upsert_entity(entity=conv)

    # === Queue Operations ===

    def get_queue_client(self, name: str):
        """Get queue client for specific queue"""
        if not AZURE_AVAILABLE:
            raise ImportError("Azure libraries are required for storage operations")
        if not self.queue_conn:
            raise EnvironmentError("No queue connection string configured")
        return QueueClient.from_connection_string(self.queue_conn, name)

    def enqueue_request(self, msg: Dict[str, Any]) -> None:
        """Enqueue agent request message"""
        if not AZURE_AVAILABLE:
            raise ImportError("Azure libraries are required for storage operations")
        q = self.get_queue_client(self.req_queue)
        q.send_message(json.dumps(msg))

    def enqueue_event(self, msg: Dict[str, Any]) -> None:
        """Enqueue agent event message"""
        if not AZURE_AVAILABLE:
            raise ImportError("Azure libraries are required for storage operations")
        q = self.get_queue_client(self.evt_queue)
        q.send_message(json.dumps(msg))

    # === Blob Storage Operations ===

    def get_blob_client(self, container: str, key: str):
        """Get blob client for specific container and key"""
        if not AZURE_AVAILABLE:
            raise ImportError("Azure libraries are required for storage operations")
        if not self.storage_conn:
            raise EnvironmentError("No storage connection string configured")
            
        if container == "mentorqa":
            blobname = f"{key}mentor_qa.jsonl"
        else:
            blobname = key
        return BlobClient.from_connection_string(
            self.storage_conn,
            container_name=container,
            blob_name=blobname
        )

    def load_json_from_blob(self, container: str, blob: str) -> Dict[str, Any]:
        """Load and parse JSON content from blob"""
        if not AZURE_AVAILABLE:
            raise ImportError("Azure libraries are required for storage operations")
        bc = BlobClient.from_connection_string(
            self.storage_conn,
            container_name=container,
            blob_name=blob
        )
        return json.loads(bc.download_blob().readall())

    def upload_mentor_qa_pair(self, domain: str, question: str, answer: str):
        """Upload mentor Q&A pair to blob storage"""
        blob = self.get_blob_client("mentorqa", domain)
        existing = ""
        if blob.exists():
            existing = blob.download_blob().readall().decode("utf-8")
        
        record = json.dumps({"question": question, "answer": answer}) + "\n"
        blob.upload_blob(existing + record, overwrite=True)

    def get_mentor_qa_pairs(self, domain: str) -> str:
        """Get all mentor Q&A pairs for a domain"""
        blob = self.get_blob_client("mentorqa", domain)
        if not blob.exists():
            return json.dumps([])
        
        data = blob.download_blob().readall().decode("utf-8").strip().splitlines()
        pairs = [json.loads(line) for line in data if line.strip()]
        return json.dumps(pairs)

    # === Agent Data Access ===

    def get_agent_dirs(self) -> Dict[str, Any]:
        """Get agent directives"""
        return self.agent_dirs or {}

    def get_agent_profiles(self) -> Dict[str, Any]:
        """Get agent profiles"""
        return self.agent_profiles or {}

    def get_domain_knowledge(self) -> Dict[str, Any]:
        """Get domain knowledge"""
        return self.domain_knowledge or {}

    # === Utility Methods ===

    def validate_configuration(self) -> Dict[str, Any]:
        """Validate storage configuration"""
        issues = []
        
        if not self.storage_conn:
            issues.append("Missing storage connection string")
        if not self.table_conn:
            issues.append("Missing table connection string")
        if not self.queue_conn:
            issues.append("Missing queue connection string")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "storage_configured": bool(self.storage_conn),
            "cosmos_configured": bool(self.cosmos_endpoint and self.cosmos_key),
            "agent_data_loaded": bool(self.agent_dirs and self.agent_profiles)
        }