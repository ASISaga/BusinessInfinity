# Customer–Seller collaboration spec

## Purpose
- **Goal:** Synchronize demand, supply, quality, and campaigns to maximize mutual value.
- **Outcome:** Lower stockouts/overstocks, higher service levels, coherent go-to-market.

## Participants
- **Buyer roles:** COO, CMO, CFO, CTO (as needed).
- **Seller roles:** COO, CMO, CFO, CTO (as needed).

## Typical use cases
- **Demand–capacity sync:** Shared forecasts and production plans.
- **Joint marketing:** Coordinated launches, promotions, and messaging.
- **Quality & compliance:** Shared audits, defect remediation.
- **Commercial terms:** Pricing models, SLAs, service credits.

## Shared artifacts
- **SharedForecast.v1:** SKU/region/time horizon with confidence bands.
- **CapacityPlan.v1:** Seller capacity slots mapped to forecast.
- **CampaignCalendar.v1:** Channel plans, offers, blackout windows.
- **QualityReport.v1:** Defect metrics, root causes, CAPAs.
- **ContractTerms.v1:** Pricing, SLAs, adjustment mechanisms.

## Decision protocol
1. **Initiation:** Buyer or seller proposes CoordinationTopic.
2. **Context:** Both sides assemble internal + shared context.
3. **Scoring:** Local Vision, Local Purpose, Partnership Value, Legendary Lens.
4. **Negotiation:** Company positions converge; trade-offs recorded.
5. **Finalization:** PartnershipAgreement.v1 + rollout plan.

## Governance & trust
- **Visibility scopes:** Role- and product-scoped access; masked PII.
- **SLAs & remedies:** Embedded in ContractTerms with automatic triggers.
- **Dispute path:** COO/CEO mediation; time-boxed; fallback arbitration.

## Data sharing & privacy
- **Data minima:** Share aggregates unless detail is necessary.
- **Freshness:** Forecast currency windows; invalidation rules.
- **Provenance:** Source system, timestamp, version.

## Observability
- **Metrics:** Forecast error, fill rate, OTIF, promo lift, defect trend.
- **Cadence:** S&OP monthly, weekly syncs during launches.

## Extensibility
- **Multi-tier propagation:** Auto-notify upstream suppliers when forecasts change.