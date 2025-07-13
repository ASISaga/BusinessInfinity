from .EnvManager import EnvManager
import datetime
import json
from azure.cosmos import CosmosClient

# Cosmos DB client setup


class CosmosManager:
    def create_conversation(self, conv_id, domain):
        container = self.get_container()
        container.create_item({
            "id": conv_id,
            "domain": domain,
            "createdAt": datetime.datetime.utcnow().isoformat(),
            "messages": []
        })

    def get_conversation(self, conv_id):
        container = self.get_container()
        try:
            conv = container.readitem(item=conv_id, partitionkey=conv_id)
            return json.dumps(conv)
        except Exception:
            return None

    def upsert_conversation(self, conv, domain=None, answer_json=None):
        if domain is not None and answer_json is not None:
            import datetime, json
            answer_obj = json.loads(answer_json)
            agent_msg = {
                "sender": domain,
                "text": answer_obj["answer"],
                "time": datetime.datetime.utcnow().isoformat()
            }
            conv["messages"].append(agent_msg)
        container = self.get_container()
        container.upsert_item(conv)
    def __init__(self):
        env = EnvManager()
        self.endpoint = env.get_required("COSMOS_ENDPOINT")
        self.key = env.get_required("COSMOS_KEY")
        self.db_name = env.get_required("COSMOSDBNAME")
        self.container_name = env.get_required("COSMOS_CONTAINER")
        self._client = None
        self._container = None

    def get_container(self):
        if self._client is None:
            self._client = CosmosClient(self.endpoint, {"masterKey": self.key})
        if self._container is None:
            db = self._client.get_database_client(self.db_name)
            self._container = db.get_container_client(self.container_name)
        return self._container
