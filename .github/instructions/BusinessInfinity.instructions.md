---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

---
## Copilot/AI Custom Instructions

### AI Context and Manifest Network
BusinessInfinity comprises of a network of modules, across the ASISaga workspace, connected via their manifest.json files. These manifests define logical relationships, dependencies, capabilities, and metadata for each module.

### Logical Structure of Business Infinity
The logical structure of the Business Infinity app is defined by its `manifest.json` file. This manifest specifies:

- The module’s metadata (such as name, version, and description).
- Its capabilities (what features or services it provides).
- Its dependencies (other modules or services it relies on).
- Relationships to other modules in the ASISaga network.

This structure enables Business Infinity to integrate seamlessly with other modules, ensures consistency, and allows for automated impact analysis and context-aware code suggestions, as outlined in these instructions. The `manifest.json` acts as the central configuration and relationship map for the Business Infinity module within the broader ASISaga ecosystem.

### Guidelines for Copilot/AI Tools

---