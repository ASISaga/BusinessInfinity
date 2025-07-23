from .EnvManager import EnvManager
import datetime
import json
from azure.data.tables import TableServiceClient, TableEntity

#

class ConversationManager:
    def create_conversation(self, conv_id, domain):
        table = self.get_table()

        entity = TableEntity()
        entity["PartitionKey"] = conv_id
        entity["RowKey"] = conv_id
        entity["domain"] = domain
        entity["createdAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        entity["messages"] = json.dumps([])
        
        table.create_entity(entity=entity)

    def get_conversation(self, conv_id):
        table = self.get_table()
        try:
            entity = table.get_entity(partition_key=conv_id, row_key=conv_id)
            entity["messages"] = json.loads(entity.get("messages", "[]"))
            return json.dumps(entity)
        except Exception:
            return None

    def upsert_conversation(self, conv, domain=None, answer_json=None):
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
        table = self.get_table()
        table.upsert_entity(entity=conv)
    def __init__(self):
        env = EnvManager()
        self.endpoint = env.get_required("COSMOS_ENDPOINT")
        self.key = env.get_required("COSMOS_KEY")
        self.table_name = env.get_required("COSMOS_CONTAINER")
        self._service_client = None
        self._table_client = None

    def get_table(self):
        if self._service_client is None:
            self._service_client = TableServiceClient(endpoint=self.endpoint, credential=self.key)
        if self._table_client is None:
            self._table_client = self._service_client.get_table_client(table_name=self.table_name)
        return self._table_client
