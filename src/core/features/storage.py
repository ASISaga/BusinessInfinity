"""
Consolidated Storage Management
Now uses AgentOperatingSystem services instead of direct Azure SDK calls
"""

import os
import json
import time
import datetime
from typing import Dict, Any, List, Optional

from AgentOperatingSystem.environment import EnvironmentManager, env_manager
from AgentOperatingSystem.storage.manager import StorageManager
from AgentOperatingSystem.messaging.servicebus_manager import ServiceBusManager
from AgentOperatingSystem.config import StorageConfig


class UnifiedStorageManager:
    """
    Business Infinity Storage Manager - uses AOS Azure services for:
    - Boardroom decision storage
    - Business metrics and KPI storage
    - Agent collaboration history
    - Business workflow state management
    """

    def __init__(self, env=None):
        # Initialize environment manager
        env_manager_instance = env or env_manager
        if isinstance(env_manager_instance, EnvironmentManager):
            self.env_manager = env_manager_instance
        else:
            self.env_manager = env_manager
        
        # Business-specific configuration
        self.boardroom_table = self.env_manager.get("BOARDROOM_TABLE_NAME", "BoardroomDecisions")
        self.metrics_table = self.env_manager.get("METRICS_TABLE_NAME", "BusinessMetrics")
        self.collaboration_table = self.env_manager.get("COLLABORATION_TABLE_NAME", "AgentCollaboration")
        self.request_queue = self.env_manager.get("REQUEST_QUEUE_NAME", "agent-requests")
        self.event_queue = self.env_manager.get("EVENT_QUEUE_NAME", "agent-events")
        
        # Initialize AOS Storage Manager
        storage_config = StorageConfig(
            storage_type="azure",
            connection_string=self.env_manager.get("AZURE_STORAGE_CONNECTION_STRING")
        )
        self.storage_manager = StorageManager(storage_config)
        
        # Initialize AOS Service Bus Manager
        servicebus_connection = self.env_manager.get("AZURE_SERVICE_BUS_CONNECTION_STRING")
        self.servicebus_manager = ServiceBusManager(servicebus_connection)
        
        # Initialize agent data (will be loaded asynchronously)
        self.agent_dirs = None
        self.agent_profiles = None
        self.domain_knowledge = None
        
        # Load agent data
        self._load_agent_data()
        
    async def store_boardroom_decision(self, decision_data: Dict[str, Any]) -> bool:
        """Store boardroom decision with audit trail"""
        try:
            # Add metadata for business context
            enhanced_data = {
                **decision_data,
                "timestamp": datetime.datetime.now().isoformat(),
                "entity_type": "boardroom_decision",
                "table_name": self.boardroom_table
            }
            
            # Use AOS storage manager to store in Azure Table
            partition_key = enhanced_data.get("PartitionKey", "BoardroomDecisions")
            row_key = enhanced_data.get("RowKey", f"decision_{int(time.time())}")
            
            result = await self.storage_manager.store_table_entity(
                table_name=self.boardroom_table,
                partition_key=partition_key,
                row_key=row_key,
                data=enhanced_data
            )
            return result.get("success", False)
        except Exception as e:
            print(f"Error storing boardroom decision: {e}")
            return False
            
    async def store_business_metrics(self, metrics: Dict[str, Any], agent_id: str) -> bool:
        """Store business metrics for an agent"""
        try:
            # Add metadata for business context
            enhanced_metrics = {
                **metrics,
                "agent_id": agent_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "entity_type": "business_metrics",
                "table_name": self.metrics_table
            }
            
            # Use AOS storage manager to store in Azure Table
            partition_key = agent_id
            row_key = f"metrics_{int(time.time())}"
            
            result = await self.storage_manager.store_table_entity(
                table_name=self.metrics_table,
                partition_key=partition_key,
                row_key=row_key,
                data=enhanced_metrics
            )
            return result.get("success", False)
        except Exception as e:
            print(f"Error storing business metrics: {e}")
            return False
            
    async def get_boardroom_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent boardroom decisions"""
        try:
            # Use AOS storage manager to query Azure Table
            query_filter = f"PartitionKey eq 'BoardroomDecisions' and entity_type eq 'boardroom_decision'"
            
            result = await self.storage_manager.query_table_entities(
                table_name=self.boardroom_table,
                query_filter=query_filter,
                select_fields=None,
                max_results=limit
            )
            
            if result.get("success", False):
                return result.get("entities", [])
            return []
        except Exception as e:
            print(f"Error getting boardroom history: {e}")
            return []

    async def initialize(self):
        """Initialize the storage manager and load agent data"""
        try:
            await self.load_agent_data_async()
            # Validate configuration
            validation_result = await self.validate_configuration()
            if not validation_result.get("success", False):
                print(f"Warning: Storage validation issues: {validation_result.get('business_requirements', [])}")
        except Exception as e:
            print(f"Warning: Storage initialization failed: {e}")

    def _load_agent_data(self):
        """Load agent data from blobs - synchronous version for backward compatibility"""
        # Placeholder for now - will be loaded asynchronously via initialize()
        self.agent_dirs = None
        self.agent_profiles = None
        self.domain_knowledge = None
        
    async def load_agent_data_async(self):
        """Load agent data from blobs using AOS storage manager"""
        try:
            directives_blob = self.env_manager.get("DIRECTIVES_BLOB")
            profiles_blob = self.env_manager.get("PROFILES_BLOB") 
            knowledge_blob = self.env_manager.get("KNOWLEDGE_BLOB")
            
            if directives_blob:
                result = await self.storage_manager.download_blob("contexts", directives_blob)
                if result.get("success", False):
                    self.agent_dirs = json.loads(result.get("content", "{}"))
                    
            if profiles_blob:
                result = await self.storage_manager.download_blob("contexts", profiles_blob)
                if result.get("success", False):
                    self.agent_profiles = json.loads(result.get("content", "{}"))
                    
            if knowledge_blob:
                result = await self.storage_manager.download_blob("knowledge", knowledge_blob)
                if result.get("success", False):
                    self.domain_knowledge = json.loads(result.get("content", "{}"))
        except Exception as e:
            print(f"Warning: Could not load agent data: {e}")

    # === Legacy Methods (deprecated - use AOS Azure services) ===
    
    def get_table_client(self):
        """Legacy method - now uses AOS Azure services internally"""
        raise NotImplementedError("Direct Azure SDK access removed. Use AOS Azure services instead.")
    
    def get_cosmos_table_client(self):
        """Legacy method - now uses AOS Azure services internally"""
        raise NotImplementedError("Direct Azure SDK access removed. Use AOS Azure services instead.")

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

    async def query_messages(self, boardroom_id: str, conversation_id: str, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query messages from table storage using AOS storage manager"""
        try:
            pk = f"{boardroom_id}|{conversation_id}"
            if since:
                query_filter = f"PartitionKey eq '{pk}' and RowKey gt '{since}'"
            else:
                query_filter = f"PartitionKey eq '{pk}'"
            
            result = await self.storage_manager.query_table_entities(
                table_name=self.collaboration_table,
                query_filter=query_filter,
                max_results=100
            )
            
            if result.get("success", False):
                entities = result.get("entities", [])
                return [self.from_row(entity) for entity in entities]
            return []
        except Exception as e:
            print(f"Error querying messages: {e}")
            return []

    # === Conversation Management ===

    async def create_conversation(self, conv_id: str, domain: str):
        """Create a new conversation using AOS storage manager"""
        try:
            entity_data = {
                "domain": domain,
                "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "messages": json.dumps([])
            }
            
            result = await self.storage_manager.store_table_entity(
                table_name=self.collaboration_table,
                partition_key=conv_id,
                row_key=conv_id,
                data=entity_data
            )
            
            if not result.get("success", False):
                raise Exception(f"Failed to create conversation: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Error creating conversation: {e}")
            raise

    async def get_conversation(self, conv_id: str) -> Optional[str]:
        """Get conversation by ID using AOS storage manager"""
        try:
            result = await self.storage_manager.get_table_entity(
                table_name=self.collaboration_table,
                partition_key=conv_id,
                row_key=conv_id
            )
            
            if result.get("success", False):
                entity = result.get("entity", {})
                entity["messages"] = json.loads(entity.get("messages", "[]"))
                return json.dumps(entity)
            return None
        except Exception:
            return None

    async def upsert_conversation(self, conv: Dict[str, Any], domain: str = None, answer_json: str = None):
        """Update conversation with new message using AOS storage manager"""
        try:
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
            
            # Extract keys and data for AOS storage manager
            partition_key = conv.get("PartitionKey")
            row_key = conv.get("RowKey")
            
            # Remove keys from data to avoid duplication
            data = {k: v for k, v in conv.items() if k not in ["PartitionKey", "RowKey"]}
            
            result = await self.storage_manager.store_table_entity(
                table_name=self.collaboration_table,
                partition_key=partition_key,
                row_key=row_key,
                data=data
            )
            
            if not result.get("success", False):
                raise Exception(f"Failed to upsert conversation: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Error upserting conversation: {e}")
            raise

    # === Queue Operations ===

    def get_queue_client(self, name: str):
        """Legacy method - now uses AOS Azure services internally"""
        raise NotImplementedError("Direct Azure SDK access removed. Use AOS Azure services instead.")

    async def enqueue_request(self, msg: Dict[str, Any]) -> None:
        """Enqueue agent request message using AOS ServiceBus manager"""
        try:
            message_content = json.dumps(msg)
            result = await self.servicebus_manager.send_message(
                queue_name=self.request_queue,
                message=message_content
            )
            
            if not result.get("success", False):
                raise Exception(f"Failed to enqueue request: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Error enqueuing request: {e}")
            raise

    async def enqueue_event(self, msg: Dict[str, Any]) -> None:
        """Enqueue agent event message using AOS ServiceBus manager"""
        try:
            message_content = json.dumps(msg)
            result = await self.servicebus_manager.send_message(
                queue_name=self.event_queue,
                message=message_content
            )
            
            if not result.get("success", False):
                raise Exception(f"Failed to enqueue event: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Error enqueuing event: {e}")
            raise

    # === Blob Storage Operations ===

    def get_blob_client(self, container: str, key: str):
        """Legacy method - now uses AOS Azure services internally"""
        raise NotImplementedError("Direct Azure SDK access removed. Use AOS Azure services instead.")

    async def load_json_from_blob(self, container: str, blob: str) -> Dict[str, Any]:
        """Load and parse JSON content from blob using AOS storage manager"""
        try:
            result = await self.storage_manager.download_blob(container, blob)
            if result.get("success", False):
                content = result.get("content")
                if isinstance(content, str):
                    return json.loads(content)
                return content or {}
            return {}
        except Exception as e:
            print(f"Error loading JSON from blob: {e}")
            return {}

    async def upload_mentor_qa_pair(self, domain: str, question: str, answer: str):
        """Upload mentor Q&A pair to blob storage using AOS storage manager"""
        try:
            qa_data = {
                "question": question,
                "answer": answer,
                "domain": domain,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            blob_name = f"{domain}/qa_pair_{int(time.time())}.json"
            content = json.dumps(qa_data)
            
            result = await self.storage_manager.upload_blob(
                container="mentors",
                blob_name=blob_name,
                data=content
            )
            
            if not result.get("success", False):
                raise Exception(f"Failed to upload Q&A pair: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Error uploading mentor Q&A pair: {e}")
            raise

    async def get_mentor_qa_pairs(self, domain: str) -> str:
        """Get all mentor Q&A pairs for a domain using AOS storage manager"""
        try:
            # List blobs in the domain directory
            result = await self.storage_manager.list_blobs("mentors", prefix=f"{domain}/")
            if not result.get("success", False):
                return json.dumps([])
            
            qa_pairs = []
            blob_names = result.get("blobs", [])
            
            # Download and parse each Q&A pair
            for blob_name in blob_names:
                if blob_name.endswith('.json'):
                    blob_result = await self.storage_manager.download_blob("mentors", blob_name)
                    if blob_result.get("success", False):
                        try:
                            qa_data = json.loads(blob_result.get("content", "{}"))
                            qa_pairs.append(qa_data)
                        except json.JSONDecodeError:
                            continue
            
            return json.dumps(qa_pairs)
        except Exception as e:
            print(f"Error getting mentor Q&A pairs: {e}")
            return json.dumps([])

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

    # === Business-Specific Operations ===

    async def get_business_metrics_by_agent(self, agent_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent business metrics for a specific agent"""
        try:
            query_filter = f"PartitionKey eq '{agent_id}' and entity_type eq 'business_metrics'"
            result = await self.storage_manager.query_table_entities(
                table_name=self.metrics_table,
                query_filter=query_filter,
                max_results=limit
            )
            
            if result.get("success", False):
                return result.get("entities", [])
            return []
        except Exception as e:
            print(f"Error getting business metrics: {e}")
            return []

    async def store_collaboration_event(self, event_data: Dict[str, Any]) -> bool:
        """Store agent collaboration event"""
        try:
            enhanced_data = {
                **event_data,
                "timestamp": datetime.datetime.now().isoformat(),
                "entity_type": "collaboration_event"
            }
            
            partition_key = event_data.get("conversation_id", "general")
            row_key = f"event_{int(time.time())}"
            
            result = await self.storage_manager.store_table_entity(
                table_name=self.collaboration_table,
                partition_key=partition_key,
                row_key=row_key,
                data=enhanced_data
            )
            return result.get("success", False)
        except Exception as e:
            print(f"Error storing collaboration event: {e}")
            return False

    async def get_recent_events(self, conversation_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent collaboration events"""
        try:
            if conversation_id:
                query_filter = f"PartitionKey eq '{conversation_id}' and entity_type eq 'collaboration_event'"
            else:
                query_filter = "entity_type eq 'collaboration_event'"
                
            result = await self.storage_manager.query_table_entities(
                table_name=self.collaboration_table,
                query_filter=query_filter,
                max_results=limit
            )
            
            if result.get("success", False):
                return result.get("entities", [])
            return []
        except Exception as e:
            print(f"Error getting recent events: {e}")
            return []

    # === Utility Methods ===

    async def validate_configuration(self) -> Dict[str, Any]:
        """Validate storage configuration using AOS services"""
        try:
            issues = []
            
            # Test storage manager connection
            try:
                test_result = await self.storage_manager.list_containers()
                if not test_result.get("success", False):
                    issues.append("Azure Storage connection failed")
            except Exception as e:
                issues.append(f"Azure Storage error: {e}")
            
            # Test service bus connection
            try:
                queue_result = await self.servicebus_manager.list_queues()
                if not queue_result.get("success", False):
                    issues.append("Azure Service Bus connection failed")
            except Exception as e:
                issues.append(f"Azure Service Bus error: {e}")
            
            # Check business-specific configuration
            business_requirements = []
            required_tables = [self.boardroom_table, self.metrics_table, self.collaboration_table]
            required_queues = [self.request_queue, self.event_queue]
            
            for table in required_tables:
                if not table:
                    business_requirements.append(f"Missing table configuration")
            
            for queue in required_queues:
                if not queue:
                    business_requirements.append(f"Missing queue configuration")
            
            return {
                "success": len(issues) == 0,
                "valid": len(issues) == 0,
                "issues": issues,
                "business_requirements": business_requirements,
                "storage_configured": len(issues) == 0,
                "agent_data_loaded": bool(self.agent_dirs and self.agent_profiles)
            }
        except Exception as e:
            return {
                "success": False,
                "valid": False,
                "issues": [f"Configuration validation failed: {e}"],
                "business_requirements": [],
                "storage_configured": False,
                "agent_data_loaded": bool(self.agent_dirs and self.agent_profiles)
            }