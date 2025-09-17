"""
Service Bus Triggers for Azure Functions

This module contains all Azure Service Bus triggers consolidated from function_app.py
and shared/framework/functions/. Updated to use consolidated core system.
"""

import json
import logging
import azure.functions as func

# Import consolidated core system
from core import api_orchestrator


def register_service_bus_triggers(app: func.FunctionApp):
    """Register all service bus trigger handlers with the FunctionApp"""
    
    # Service Bus trigger function for decision events (consolidated from function_app.py and shared/framework/)
    @app.service_bus_topic_trigger(arg_name="msg", topic_name="bi-events", 
                                  subscription_name="governance",
                                  connection="AZURE_SERVICE_BUS_CONNECTION_STRING")
    def process_decision_event(msg: func.ServiceBusMessage):
        """Process decision events from service bus using consolidated API orchestrator"""
        try:
            body = msg.get_body().decode("utf-8")
            subject = msg.subject
            logging.info(f"[GOV] Event: {subject} Payload: {body}")
            
            # Use consolidated API orchestrator to handle the message
            result = api_orchestrator.handle_servicebus_message(body)
            
            if result:
                logging.info(f"Successfully processed service bus message: {subject}")
            else:
                logging.warning(f"Failed to process service bus message: {subject}")
                
        except Exception as e:
            logging.error(f"Error processing service bus message: {e}")
            raise

    # Service Bus queue trigger (consolidated from api/router.py)
    @app.service_bus_queue_trigger(arg_name="msg", queue_name="myqueue", 
                                  connection="AzureServiceBusConnection")
    def servicebus_queue_trigger(msg: func.ServiceBusMessage):
        """Process Service Bus queue messages"""
        try:
            message_body = msg.get_body().decode('utf-8')
            logging.info(f"Received Service Bus queue message: {message_body}")
            
            # Use consolidated API orchestrator to handle the message
            result = api_orchestrator.handle_servicebus_message(message_body)
            
            if result:
                logging.info("Successfully processed service bus queue message")
            else:
                logging.warning("Failed to process service bus queue message")
                
        except Exception as e:
            logging.error(f"Error processing service bus queue message: {e}")
            raise