You are to act as the schema designer for my application-level manifest.json, which you will manage and consume.
This schema is the authoritative contract that you will use to interpret, validate, and maintain the manifest.
Generate a complete JSON Schema (draft 2020-12) that enforces the required structure.

Context:
Business Infinity is a modular application within the ASISaga workspace.
- Python modules use pyproject.toml as their manifest.
- Jekyll modules use _config.yml as their manifest.
- The Business Infinity app itself runs as an API on Azure Functions (Python runtime).
- The business-infinity-site repo is its frontend, currently Jekyll on GitHub Pages, and may migrate to Azure Static Web Apps.
- A shared theme repo provides design consistency across sites.
- The root manifest.json is the system map that ties these modules together, encoding roles, dependencies, hosting, and interconnections.

Schema requirements:
- application: { name, version, description }
- python_packages: object of packages, each with { path, manifest, role, depends_on[] }
- websites: object of sites, each with { path, manifest, type, role, hosted_on, frontend_for?, depends_on[] }
- themes: object of themes, each with { path, role, type, used_by[] }
- apis: object of services, each with { path, manifest, role, runtime, language, exposed_endpoints[], consumed_by[] }
- cross_dependencies: array of { from, to, type }

Rules:
- Roles must be restricted to: ["frontend", "backend", "api", "library", "theme"].
- Required fields must be enforced for each section.
- Types must be validated (arrays of strings, enums for role and type).
- Reject unrecognized properties to prevent drift.

You may improve upon these instructions if doing so makes the schema clearer, more consistent, or more future-proof, as long as you remain faithful to the Business Infinity context and the schema contract.
Output only the JSON Schema.