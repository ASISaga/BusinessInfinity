import json
import logging
import azure.functions as func

def main(msg: func.ServiceBusMessage):
    body = msg.get_body().decode("utf-8")
    subject = msg.subject
    logging.info(f"[GOV] Event: {subject} Payload: {body}")
    # Add side effects: persist to Cosmos DB, trigger notifications, etc.