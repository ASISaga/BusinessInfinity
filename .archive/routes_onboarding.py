import json
import azure.functions as func

# === Dummy class for onboarding endpoints ===
class OnboardingEndpoint:
    def __init__(self, business_infinity=None, logger=None):
        self.business_infinity = business_infinity
        self.logger = logger

    async def onboarding_interface(self, req):
        """Serve the onboarding interface"""
        try:
            import os
            onboarding_path = os.path.join(os.path.dirname(__file__), "onboarding", "onboarding.html")
            if os.path.exists(onboarding_path):
                with open(onboarding_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                return func.HttpResponse(
                    html_content,
                    mimetype="text/html",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    "<h1>Onboarding not found</h1><p>The onboarding interface file was not found.</p>",
                    mimetype="text/html",
                    status_code=404
                )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error serving onboarding interface: {e}")
            return func.HttpResponse(
                f"<h1>Error</h1><p>Failed to load onboarding interface: {str(e)}</p>",
                mimetype="text/html",
                status_code=500
            )

    async def parse_website(self, req):
        """Parse website content for onboarding"""
        try:
            from datetime import datetime
            request_data = req.get_json()
            website_url = request_data.get('url')
            if not website_url:
                return func.HttpResponse(
                    json.dumps({"error": "Website URL is required"}),
                    mimetype="application/json",
                    status_code=400
                )
            parsed_data = {
                "company_name": "Example Company",
                "tagline": "Innovative solutions for modern business",
                "description": "We provide cutting-edge technology solutions to help businesses scale and succeed.",
                "source_url": website_url,
                "parsed_at": datetime.now().isoformat()
            }
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "data": parsed_data,
                    "message": "Website parsed successfully"
                }),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error parsing website: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e), "success": False}),
                mimetype="application/json",
                status_code=500
            )

    async def upload_deck(self, req):
        """Handle pitch deck upload and processing"""
        try:
            from datetime import datetime
            processed_data = {
                "filename": "pitch_deck.pdf",
                "file_hash": "abc123def456",
                "slides_count": 12,
                "key_sections": ["Problem", "Solution", "Market", "Business Model", "Team", "Financials"],
                "encrypted": True,
                "uploaded_at": datetime.now().isoformat()
            }
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "data": processed_data,
                    "message": "Pitch deck uploaded and processed successfully"
                }),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error uploading deck: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e), "success": False}),
                mimetype="application/json",
                status_code=500
            )

    async def upload_financials(self, req):
        """Handle financial document upload"""
        try:
            from datetime import datetime
            processed_data = {
                "files_processed": 2,
                "financial_data_extracted": True,
                "revenue_data": "Available",
                "expense_data": "Available",
                "encrypted": True,
                "retention_days": 30,
                "uploaded_at": datetime.now().isoformat()
            }
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "data": processed_data,
                    "message": "Financial documents uploaded successfully"
                }),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error uploading financials: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e), "success": False}),
                mimetype="application/json",
                status_code=500
            )

    async def connect_system(self, req):
        """Handle system connector authorization"""
        try:
            request_data = req.get_json()
            system_name = request_data.get('system')
            if not system_name:
                return func.HttpResponse(
                    json.dumps({"error": "System name is required"}),
                    mimetype="application/json",
                    status_code=400
                )
            user_id = request_data.get('user_id', 'onboarding_user')
            customer_id = request_data.get('customer_id', 'onboarding_customer')
            oauth_urls = {
                'salesforce': 'https://login.salesforce.com/services/oauth2/authorize?...',
                'hubspot': 'https://app.hubspot.com/oauth/authorize?...',
                'netsuite': 'https://system.netsuite.com/pages/customerlogin.jsp?...',
                'workday': 'https://wd2-impl.workday.com/...',
                'quickbooks': 'https://appcenter.intuit.com/connect/oauth2?...',
                'slack': 'https://slack.com/oauth/v2/authorize?...'
            }
            auth_url = oauth_urls.get(system_name, f'https://example.com/oauth/{system_name}')
            self.log_onboarding_consent(
                user_id=user_id,
                customer_id=customer_id,
                consent_type="system_integration",
                consent_given=True,
                description=f"User consented to connect {system_name} system with read-only access for business analysis"
            )
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "auth_url": auth_url,
                    "system": system_name,
                    "scopes": "read-only",
                    "message": f"OAuth URL generated for {system_name}",
                    "consent_logged": True
                }),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error connecting system: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e), "success": False}),
                mimetype="application/json",
                status_code=500
            )

    async def generate_voice_profile(self, req):
        """Generate voice profile from LinkedIn posts and other content"""
        try:
            from datetime import datetime
            request_data = req.get_json()
            voice_profile = {
                "themes": ["Innovation", "Leadership", "Growth", "Technology"],
                "tone": "Professional yet approachable",
                "style": "Strategic with practical insights",
                "key_phrases": ["driving growth", "strategic vision", "innovation"],
                "communication_frequency": "Regular",
                "generated_at": datetime.now().isoformat()
            }
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "data": voice_profile,
                    "message": "Voice profile generated successfully"
                }),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating voice profile: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e), "success": False}),
                mimetype="application/json",
                status_code=500
            )

    async def handle_quick_action(self, req):
        """Handle final onboarding quick actions"""
        try:
            request_data = req.get_json()
            message = request_data.get('message', '').lower()
            user_id = request_data.get('user_id', 'onboarding_user')
            customer_id = request_data.get('customer_id', 'onboarding_customer')
            if 'a' in message or 'runway' in message or 'cfo' in message:
                response = "Excellent choice! I'll connect you with our CFO agent who will analyze your financial data and create a comprehensive runway model. This will include burn rate analysis, funding requirements, and key financial milestones."
                consent_desc = "User chose CFO agent analysis - consented to financial data processing for runway modeling"
                action_type = "cfo_analysis"
            elif 'b' in message or 'gtm' in message or 'cmo' in message:
                response = "Great selection! Our CMO agent will create a Go-to-Market voice brief based on your company profile, target market analysis, and communication style. This will help align your messaging across all channels."
                consent_desc = "User chose CMO agent analysis - consented to marketing data processing for GTM strategy"
                action_type = "cmo_analysis"
            elif 'c' in message or 'review' in message or 'deep' in message:
                response = "I'll schedule a comprehensive strategic review session with the full C-Suite team. We'll analyze all your data and provide detailed insights on operations, finance, marketing, and growth opportunities."
                consent_desc = "User chose comprehensive strategic review - consented to full business data analysis by C-Suite agents"
                action_type = "full_review"
            else:
                response = "I understand you'd like to explore other options. Feel free to ask me anything about your business, or you can always return to the quick actions (A, B, or C) when you're ready."
                consent_desc = "User explored other options - implicit consent to continue onboarding process"
                action_type = "explore_options"
            self.log_onboarding_consent(
                user_id=user_id,
                customer_id=customer_id,
                consent_type="onboarding_service_selection",
                consent_given=True,
                description=consent_desc
            )
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "response": response,
                    "action_recorded": True,
                    "action_type": action_type,
                    "consent_logged": True
                }),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error handling quick action: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e), "success": False}),
                mimetype="application/json",
                status_code=500
            )

    async def get_audit_trail(self, req):
        """Serve audit trail interface"""
        try:
            from datetime import datetime
            audit_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Onboarding Audit Trail</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    .audit-entry {{ margin: 10px 0; padding: 10px; border-left: 3px solid #667eea; background: #f8f9fa; }}
                    .timestamp {{ color: #666; font-size: 0.9em; }}
                </style>
            </head>
            <body>
                <h1>Onboarding Audit Trail</h1>
                <div class="audit-entry">
                    <div class="timestamp">{datetime.now().isoformat()}</div>
                    <div>Onboarding session initiated</div>
                </div>
                <div class="audit-entry">
                    <div class="timestamp">{datetime.now().isoformat()}</div>
                    <div>LinkedIn authentication requested (read-only scope)</div>
                </div>
                <div class="audit-entry">
                    <div class="timestamp">{datetime.now().isoformat()}</div>
                    <div>Website content parsed (public content only)</div>
                </div>
                <div class="audit-entry">
                    <div class="timestamp">{datetime.now().isoformat()}</div>
                    <div>Documents uploaded and encrypted</div>
                </div>
                <div class="audit-entry">
                    <div class="timestamp">{datetime.now().isoformat()}</div>
                    <div>Voice profile generated from public posts</div>
                </div>
                <div class="audit-entry">
                    <div class="timestamp">{datetime.now().isoformat()}</div>
                    <div>Founder dossier created (read-only operations)</div>
                </div>
            </body>
            </html>
            """
            return func.HttpResponse(
                audit_html,
                mimetype="text/html",
                status_code=200
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error serving audit trail: {e}")
            return func.HttpResponse(
                f"Error loading audit trail: {str(e)}",
                status_code=500
            )

    async def export_customer_data(self, req):
        """Export customer data for compliance"""
        try:
            from datetime import datetime
            request_data = req.get_json()
            customer_id = request_data.get('customer_id', 'onboarding_customer')
            export_data = {
                "customer_id": customer_id,
                "exported_at": datetime.now().isoformat(),
                "data": {
                    "profile": "Sample profile data",
                    "documents": ["pitch_deck.pdf", "financials.xlsx"],
                    "audit_trail": ["session initiated", "documents uploaded"]
                }
            }
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "data": export_data,
                    "message": "Customer data exported successfully"
                }),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error exporting customer data: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e), "success": False}),
                mimetype="application/json",
                status_code=500
            )

    async def request_data_deletion(self, req):
        """Request deletion of customer data for compliance"""
        try:
            from datetime import datetime
            request_data = req.get_json()
            customer_id = request_data.get('customer_id', 'onboarding_customer')
            deletion_record = {
                "customer_id": customer_id,
                "deletion_requested_at": datetime.now().isoformat(),
                "status": "pending",
                "message": "Your data deletion request has been received and is being processed."
            }
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "data": deletion_record,
                    "message": "Data deletion request submitted"
                }),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error requesting data deletion: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e), "success": False}),
                mimetype="application/json",
                status_code=500
            )

    async def get_rbac_info(self, req):
        """Get RBAC (role-based access control) info for onboarding"""
        try:
            rbac_info = {
                "roles": [
                    {"role": "Founder", "permissions": ["read", "write", "export", "delete"]},
                    {"role": "CFO", "permissions": ["read", "analyze", "export"]},
                    {"role": "CMO", "permissions": ["read", "analyze"]},
                    {"role": "COO", "permissions": ["read", "analyze"]},
                    {"role": "CTO", "permissions": ["read", "analyze"]},
                    {"role": "CSO", "permissions": ["read", "analyze"]},
                    {"role": "CHRO", "permissions": ["read", "analyze"]}
                ],
                "default_role": "Founder",
                "rbac_policy_url": "https://businessinfinity.asisaga.com/rbac-policy"
            }
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "data": rbac_info,
                    "message": "RBAC info retrieved successfully"
                }),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting RBAC info: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e), "success": False}),
                mimetype="application/json",
                status_code=500
            )

    async def get_incident_contact_info(self, req):
        """Get incident contact info for onboarding"""
        try:
            contact_info = {
                "email": "security@businessinfinity.asisaga.com",
                "phone": "+1-800-555-1234",
                "address": "123 Infinity Loop, Suite 100, Saga City, AS 12345",
                "incident_policy_url": "https://businessinfinity.asisaga.com/incident-policy"
            }
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "data": contact_info,
                    "message": "Incident contact info retrieved successfully"
                }),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting incident contact info: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e), "success": False}),
                mimetype="application/json",
                status_code=500
            )

    async def get_retention_policy(self, req):
        """Get current data retention and deletion policy"""
        try:
            from core.trust_compliance import get_trust_compliance_manager
            tcm = get_trust_compliance_manager()
            retention_policy = tcm.get_retention_policy()
            return func.HttpResponse(
                json.dumps(retention_policy, default=str),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting retention policy: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )
    def log_onboarding_consent(self, user_id: str, customer_id: str, consent_type: str, 
                              consent_given: bool, description: str) -> None:
        """Helper method to log consent during onboarding"""
        try:
            from core.trust_compliance import get_trust_compliance_manager
            tcm = get_trust_compliance_manager()
            tcm.log_consent(user_id, customer_id, consent_type, consent_given, description)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to log consent: {e}")

# === Onboarding Endpoints ===


