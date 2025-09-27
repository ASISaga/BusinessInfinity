You are to act as the maintainer of my application-level manifest.json. 
Here is the JSON Schema that defines its structure: [PASTE SCHEMA HERE]. 
Here is the current manifest.json: [PASTE MANIFEST HERE].

Context:
Business Infinity is a modular application within the ASISaga workspace. 
- Python modules use pyproject.toml as their manifest. 
- Jekyll modules use _config.yml as their manifest. 
- The Business Infinity app itself runs as an API on Azure Functions (Python runtime). 
- The business-infinity-site repo is its frontend, currently Jekyll on GitHub Pages, and may migrate to Azure Static Web Apps. 
- A shared theme repo provides design consistency across sites. 
- The root manifest.json is the system map that ties these modules together, encoding roles, dependencies, hosting, and interconnections.

Task:
Update the manifest according to these dynamic changes in the application setup:
- [Describe the changes, e.g. "Migrate business-infinity-site from GitHub Pages to Azure Static Web Apps"]
- [Add/remove/edit Python packages, websites, APIs, or themes as needed]

You must validate the updated manifest against the schema before returning it. 
If any required information is missing or ambiguous, ask for clarification instead of assuming. 
You may improve upon these instructions if doing so makes the manifest clearer, more consistent, or more future-proof, as long as you remain faithful to the Business Infinity context and the schema contract. 
Output only the corrected manifest.json.