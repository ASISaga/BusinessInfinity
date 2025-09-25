---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

---
## Copilot/AI Custom Instructions

### AI Context and Manifest Network
BusinessInfinity comprises of a network of modules, across the ASISaga workspace, connected via their manifest.json files. These manifests define logical relationships, dependencies, capabilities, and metadata for each module.

### Guidelines for Copilot/AI Tools
- Aggregate and interpret manifest.json metadata for this module and its dependencies.
- Recognize and reason about module relationships, dependencies, and capabilities as described in manifests.
- Support context-aware code suggestions, navigation, and documentation based on manifest data.
- Enable automated impact analysis when changes are made to this module or its dependencies.
- Surface module capabilities, version, and related modules for AI-driven workflows.
- When generating code or documentation, leverage the manifest network to ensure consistency and integration across modules.

---