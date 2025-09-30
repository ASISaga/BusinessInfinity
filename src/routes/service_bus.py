import json
import azure.functions as func

class ServiceBusEndpoint:
    def __init__(self, business_infinity=None, logger=None):
        self.business_infinity = business_infinity
        self.logger = logger

    async def process_decision_queue(self, msg: func.ServiceBusMessage) -> None:
        """Process decisions from Service Bus queue"""
        try:
            message_body = msg.get_body().decode('utf-8')
            decision_context = json.loads(message_body)
            if self.logger:
                self.logger.info(f"Processing decision from queue: {decision_context}")
            if self.business_infinity:
                result = await self.business_infinity.make_strategic_decision(decision_context)
                if self.logger:
                    self.logger.info(f"Decision result: {result}")
            else:
                if self.logger:
                    self.logger.warning("Business Infinity not available for queue processing")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error processing decision queue message: {e}")

    async def process_business_events(self, msg: func.ServiceBusMessage) -> None:
        """Process business events from Service Bus topic"""
        try:
            message_body = msg.get_body().decode('utf-8')
            event_data = json.loads(message_body)
            event_type = event_data.get('type', 'unknown')
            if self.logger:
                self.logger.info(f"Processing business event: {event_type}")
            if self.business_infinity and event_type in ['workflow_request', 'agent_task']:
                workflow_name = event_data.get('workflow', 'generic')
                workflow_params = event_data.get('params', {})
                workflow_id = await self.business_infinity.execute_business_workflow(workflow_name, workflow_params)
                if self.logger:
                    self.logger.info(f"Started workflow {workflow_id} for event {event_type}")
            else:
                if self.logger:
                    self.logger.info(f"Event {event_type} processed (no action required)")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error processing business event: {e}")
