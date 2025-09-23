# Mentor Mode Boardroom LLM Control (VS Code Extension)

## Overview
Mentor Mode is a **VS Code extension** designed for developers working on the **BusinessInfinity Boardroom of Agents**.  
It provides a unified control surface to **test, fine‑tune, monitor, and deploy** per‑agent **LoRA adapters** hosted on **Azure Machine Learning (AML)**, with orchestration via **Azure Functions**.

This extension integrates directly into the VS Code **Language Model Chat** interface, allowing you to:
- Chat with any Boardroom agent’s current LoRA model.
- Trigger fine‑tuning jobs from inside VS Code.
- Stream training logs in real‑time.
- Deploy updated adapters to production.

---

## Features
- **Agent Selector**: Browse all Boardroom agents and their LoRA versions.
- **Chat Interface**: Send prompts and receive streamed responses from AML endpoints.
- **Fine‑Tuning Control**: Start LoRA training jobs via Azure Functions.
- **Training Log Streaming**: View AML job logs in VS Code’s output panel.
- **Adapter Deployment**: Push new LoRA versions to the Boardroom registry.
- **Version Comparison**: Test outputs from different LoRA versions side‑by‑side.

---