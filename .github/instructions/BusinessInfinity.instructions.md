---
applyTo: '**'
---

BusinessInfinity is a modular application in the ASISaga workspace.
- Python modules use pyproject.toml as their manifest.
- Jekyll modules use _config.yml as their manifest.
- The BusinessInfinity app runs as an API on Azure Functions (Python runtime).
- The businessinfinity.asisaga.com repo is its frontend, currently Jekyll on GitHub Pages.
- A shared theme repo provides design consistency across sites.
- The root manifest.json is the AI-managed system map that ties modules together, encoding roles, dependencies, hosting, and interconnections.

Schema Enforcement
- A JSON Schema defines the authoritative structure of manifest.json.
- Always validate manifest.json against this schema before returning updates.
- If required information is missing or ambiguous, ask for clarification instead of assuming.
- You may improve schema, if it makes the manifest clearer, more consistent, or more future-proof, as long as you remain faithful to the schema and Business Infinity context.

Guidelines
- Roles: every module must declare one of: frontend, backend, api, library, theme.
- Dependencies: only internal logical dependencies are listed in manifest.json; external packages remain in pyproject.toml or _config.yml.
- Hosting: websites declare hosted_on (e.g. GitHub Pages, Azure Static Web Apps).
- Frontends: may declare frontend_for to link explicitly to their backend/API.

Python Dependencies
- Remote: declared in pyproject.toml as Git URLs for CI/CD.
- Local: install with pip install -e . (or uv pip install -e .) to create .pth links for development.