import json
import logging

class BusinessServiceBusHandlers:
    def __init__(self, business_infinity, logger=None):
        self.business_infinity = business_infinity
        self.logger = logger or logging.getLogger(__name__)

    async def business_decision_processor(self, msg):
        try:
            if not self.business_infinity:
                self.logger.warning("Business decision received but Business Infinity not available")
                return
            await self.business_infinity._initialize_task
            decision_context = json.loads(msg.get_body().decode('utf-8'))
            decision_result = await self.business_infinity.make_strategic_decision(decision_context)
            self.logger.info(f"Processed business decision: {decision_result.get('id', 'unknown')}")
        except Exception as e:
            self.logger.error(f"Business decision processing failed: {e}")

    async def business_event_processor(self, msg):
        try:
            if not self.business_infinity_available or not self.business_infinity:
                self.logger.warning("Business event received but Business Infinity not available")
                return
            await self.business_infinity._initialize_task
            event_data = json.loads(msg.get_body().decode('utf-8'))
            event_type = event_data.get('type', 'unknown')
            self.logger.info(f"Processing business event: {event_type}")
            if event_type == "performance_metric":
                await self._process_performance_metric(event_data)
            elif event_type == "business_milestone":
                await self._process_business_milestone(event_data)
            elif event_type == "external_integration":
                await self._process_external_integration(event_data)
        except Exception as e:
            self.logger.error(f"Business event processing failed: {e}")

    async def _process_performance_metric(self, event_data):
        if self.business_infinity and self.business_infinity.analytics_engine:
            metric_name = event_data.get('metric_name')
            metric_value = event_data.get('metric_value')
            metric_unit = event_data.get('metric_unit', 'count')
            if metric_name and metric_value is not None:
                await self.business_infinity.analytics_engine.record_metric(
                    name=metric_name,
                    value=metric_value,
                    unit=metric_unit,
                    metric_type="external"
                )

    async def _process_business_milestone(self, event_data):
        milestone = event_data.get('milestone')
        self.logger.info(f"Business milestone achieved: {milestone}")
        # Could trigger celebration workflow or stakeholder notifications

    async def _process_external_integration(self, event_data):
        integration_type = event_data.get('integration_type')
        self.logger.info(f"External integration event: {integration_type}")
        # Could trigger data synchronization or workflow updates
