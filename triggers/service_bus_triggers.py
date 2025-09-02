"""
Service Bus Triggers for Azure Functions

This module contains all Azure Service Bus triggers consolidated from function_app.py
and shared/framework/functions/
"""

import json
import logging
import azure.functions as func


def register_service_bus_triggers(app: func.FunctionApp):
    """Register all service bus trigger handlers with the FunctionApp"""
    
    # Service Bus trigger function for decision events (consolidated from function_app.py and shared/framework/)
    @app.service_bus_topic_trigger(arg_name="msg", topic_name="bi-events", 
                                  subscription_name="governance",
                                  connection="AZURE_SERVICE_BUS_CONNECTION_STRING")
    def process_decision_event(msg: func.ServiceBusMessage):
        """Process decision events from service bus"""
        body = msg.get_body().decode("utf-8")
        subject = msg.subject
        logging.info(f"[GOV] Event: {subject} Payload: {body}")
        # Add side effects: persist to Cosmos DB, trigger notifications, etc.
        
        # Additional processing can be added here
        try:
            # Parse the message body if it's JSON
            if body:
                payload = json.loads(body) if body.strip().startswith('{') else body
                logging.info(f"[GOV] Processed payload type: {type(payload)}")
        except json.JSONDecodeError as e:
            logging.warning(f"[GOV] Non-JSON payload received: {e}")
        except Exception as e:
            logging.error(f"[GOV] Error processing decision event: {e}")


    # Example service bus queue trigger (from api/router.py)
    # This can be uncommented and configured if needed
    # @app.service_bus_queue_trigger(arg_name="msg", queue_name="myqueue", 
    #                               connection="AzureServiceBusConnection")
    # def servicebus_queue_trigger(msg: func.ServiceBusMessage):
    #     """Process Service Bus queue messages"""
    #     message_body = msg.get_body().decode('utf-8')
    #     logging.info(f"Received Service Bus queue message: {message_body}")
    #     # Add custom handling logic here