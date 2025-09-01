import os, json
from azure.servicebus import ServiceBusClient, ServiceBusMessage

class Bus:
    def __init__(self):
        self.conn = os.environ["AZURE_SERVICE_BUS_CONNECTION_STRING"]
        self.topic = os.getenv("AZURE_SERVICE_BUS_TOPIC", "bi-events")
        self.client = ServiceBusClient.from_connection_string(self.conn, logging_enable=False)

    def publish(self, subject: str, payload: dict):
        with self.client:
            sender = self.client.get_topic_sender(topic_name=self.topic)
            with sender:
                msg = ServiceBusMessage(json.dumps(payload), subject=subject, content_type="application/json")
                sender.send_messages(msg)