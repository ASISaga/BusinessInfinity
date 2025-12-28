import azure.functions as func
import json

class AuditEndpoint:
    def __init__(self, audit_viewer):
        self.audit_viewer = audit_viewer

    async def report(self, req: func.HttpRequest) -> func.HttpResponse:
        try:
            if not self.audit_viewer:
                return func.HttpResponse(
                    json.dumps({"error": "Audit viewer not available"}),
                    mimetype="application/json",
                    status_code=503
                )
            days = int(req.params.get("days", 7))
            report = await self.audit_viewer.generate_business_report(days)
            return func.HttpResponse(
                json.dumps(report, default=str),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def decisions(self, req: func.HttpRequest) -> func.HttpResponse:
        try:
            if not self.audit_viewer:
                return func.HttpResponse(
                    json.dumps({"error": "Audit viewer not available"}),
                    mimetype="application/json",
                    status_code=503
                )
            days = int(req.params.get("days", 7))
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            decisions = await self.audit_viewer.view_business_decisions(start_date, end_date)
            return func.HttpResponse(
                json.dumps({
                    "decisions": decisions,
                    "period": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat(),
                        "days": days
                    },
                    "total": len(decisions)
                }, default=str),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )
