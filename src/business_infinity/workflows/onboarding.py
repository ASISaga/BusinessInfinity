"""Onboarding workflows for BusinessInfinity.

Handles the founder onboarding journey: website parsing, external-system
connection via OAuth, founder voice-profile generation, and GDPR
data-portability / right-to-erasure requests.
"""

from __future__ import annotations

from typing import Any, Dict

from aos_client import WorkflowRequest

from ._app import app, logger

_ONBOARDING_CONSENT_DOC_TYPE = "onboarding-consent"

#: OAuth entry-point URLs for each supported integration system.
_OAUTH_URLS: Dict[str, str] = {
    "salesforce": "https://login.salesforce.com/services/oauth2/authorize",
    "hubspot": "https://app.hubspot.com/oauth/authorize",
    "netsuite": "https://system.netsuite.com/pages/customerlogin.jsp",
    "workday": "https://wd2-impl.workday.com/",
    "quickbooks": "https://appcenter.intuit.com/connect/oauth2",
    "slack": "https://slack.com/oauth/v2/authorize",
}


@app.workflow("onboarding-parse-website")
async def onboarding_parse_website(request: WorkflowRequest) -> Dict[str, Any]:
    """Parse a company website during onboarding to extract profile data.

    Request body::

        {"url": "https://example.com"}
    """
    from datetime import datetime as dt, timezone

    if "url" not in request.body:
        raise ValueError("url is required")

    website_url: str = request.body["url"]
    # Ask the CEO agent to summarise the company based on the public URL
    response = await request.client.ask_agent(
        agent_id="ceo",
        message=f"Summarise the company at {website_url} for onboarding purposes.",
        context={"source_url": website_url},
    )
    description = (
        response.model_dump(mode="json") if hasattr(response, "model_dump") else str(response)
    )
    parsed_data: Dict[str, Any] = {
        "source_url": website_url,
        "description": description,
        "parsed_at": dt.now(timezone.utc).isoformat(),
    }

    # Persist as a knowledge-base document
    await request.client.create_document({
        "doc_type": "onboarding-profile",
        "title": f"Onboarding profile: {website_url}",
        **parsed_data,
    })
    logger.info("Onboarding website parsed: %s", website_url)
    return {"success": True, "data": parsed_data}


@app.workflow("onboarding-connect-system")
async def onboarding_connect_system(request: WorkflowRequest) -> Dict[str, Any]:
    """Generate an OAuth authorization URL to connect an external system.

    Logs the user's consent decision in the audit trail before returning
    the redirect URL.

    Request body::

        {
            "system": "salesforce",
            "user_id": "founder-001",
            "customer_id": "cust-001"
        }
    """
    if "system" not in request.body:
        raise ValueError("system is required")

    system_name: str = request.body["system"]
    user_id: str = request.body.get("user_id", "onboarding_user")
    customer_id: str = request.body.get("customer_id", "onboarding_customer")
    auth_url: str = _OAUTH_URLS.get(system_name, f"https://example.com/oauth/{system_name}")

    # Log consent in the audit trail
    await request.client.log_decision({
        "title": f"Onboarding consent: connect {system_name}",
        "rationale": f"User {user_id} consented to connect {system_name} with read-only access",
        "agent_id": user_id,
        "customer_id": customer_id,
        "consent_type": "system_integration",
    })

    logger.info("OAuth URL generated for system %s (user %s)", system_name, user_id)
    return {
        "success": True,
        "auth_url": auth_url,
        "system": system_name,
        "scopes": "read-only",
        "consent_logged": True,
    }


@app.workflow("onboarding-voice-profile")
async def onboarding_voice_profile(request: WorkflowRequest) -> Dict[str, Any]:
    """Generate a founder voice profile from LinkedIn and public content.

    Asks the CMO agent to analyse the founder's communication style and
    stores the resulting profile in the knowledge base.

    Request body::

        {"linkedin_url": "https://linkedin.com/in/jsmith", "company_name": "Acme"}
    """
    from datetime import datetime as dt, timezone

    linkedin_url: str = request.body.get("linkedin_url", "")
    company_name: str = request.body.get("company_name", "")

    response = await request.client.ask_agent(
        agent_id="cmo",
        message=(
            f"Analyse the founder's voice and communication style based on their LinkedIn "
            f"profile at {linkedin_url} for company '{company_name}'. "
            "Return themes, tone, style, and key phrases."
        ),
        context={"linkedin_url": linkedin_url, "company_name": company_name},
    )
    profile_data = (
        response.model_dump(mode="json") if hasattr(response, "model_dump") else str(response)
    )
    voice_profile: Dict[str, Any] = {
        "linkedin_url": linkedin_url,
        "company_name": company_name,
        "profile": profile_data,
        "generated_at": dt.now(timezone.utc).isoformat(),
    }
    await request.client.create_document({
        "doc_type": "onboarding-voice-profile",
        "title": f"Voice profile: {company_name}",
        **voice_profile,
    })
    logger.info("Voice profile generated for %s", company_name)
    return {"success": True, "data": voice_profile}


@app.workflow("onboarding-export-data")
async def onboarding_export_data(request: WorkflowRequest) -> Dict[str, Any]:
    """Export all onboarding data for a customer (GDPR data portability).

    Retrieves onboarding-related documents from the knowledge base and
    returns them as a structured export bundle.

    Request body::

        {"customer_id": "cust-001"}
    """
    from datetime import datetime as dt, timezone

    if "customer_id" not in request.body:
        raise ValueError("customer_id is required")

    customer_id: str = request.body["customer_id"]
    docs = await request.client.search_documents(
        query=customer_id,
        doc_type="onboarding-profile",
        limit=50,
    )
    exported = [
        d.model_dump(mode="json") if hasattr(d, "model_dump") else dict(d)
        for d in docs
    ]
    logger.info("Exported %d onboarding documents for customer %s", len(exported), customer_id)
    return {
        "customer_id": customer_id,
        "exported_at": dt.now(timezone.utc).isoformat(),
        "data": {"documents": exported},
    }


@app.workflow("onboarding-delete-data")
async def onboarding_delete_data(request: WorkflowRequest) -> Dict[str, Any]:
    """Submit a data-deletion request for a customer (GDPR right to erasure).

    Logs the deletion request in the audit trail so compliance teams can
    action it.

    Request body::

        {"customer_id": "cust-001", "user_id": "founder-001"}
    """
    from datetime import datetime as dt, timezone

    if "customer_id" not in request.body:
        raise ValueError("customer_id is required")

    customer_id: str = request.body["customer_id"]
    user_id: str = request.body.get("user_id", customer_id)

    await request.client.log_decision({
        "title": f"Data deletion request: customer {customer_id}",
        "rationale": "GDPR right-to-erasure request submitted via onboarding-delete-data workflow",
        "agent_id": user_id,
        "customer_id": customer_id,
    })
    requested_at = dt.now(timezone.utc).isoformat()
    logger.info("Data deletion request submitted for customer %s", customer_id)
    return {
        "customer_id": customer_id,
        "deletion_requested_at": requested_at,
        "status": "pending",
        "message": "Your data deletion request has been received and is being processed.",
    }
