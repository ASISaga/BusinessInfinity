┌──────────────────────────────────────────────────────────────────────────────┐
 │                              Frontend: Boardroom                             │
 │──────────────────────────────────────────────────────────────────────────────│
 │  • Chat UI (polls host for messages)                                          │
 │  • Dashboard (renders MCP‑UI schema from host)                                │
 │  • Demo/Training UI (calls host AML APIs)                                     │
 └──────────────────────────────────────────────────────────────────────────────┘
                │
                ▼
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │                  Azure Functions Host App  (Consumption Plan)                 │
 │──────────────────────────────────────────────────────────────────────────────│
 │  MCP‑UI Module                                                                │
 │    • Reads manifest.mcpUi (role/scope)                                        │
 │    • Generates UI schema for dashboard                                        │
 │    • Maps UI actions → SK agent calls                                         │
 │                                                                                │
 │  Governance / Validation Layer                                                │
 │    • Role/scope/tool checks                                                    │
 │    • Policy engine (OPA/Cedar)                                                 │
 │                                                                                │
 │  AML Manager                                                                   │
 │    • Start/stop AML Online Endpoints                                           │
 │    • Route inference calls to correct LoRA adapter                            │
 │    • Trigger LoRA training jobs (demo or production)                          │
 │    • Monitor job status & push results                                        │
 │                                                                                │
 │  Persistence                                                                   │
 │    • Azure Table Storage (PartitionKey=boardroomId, RowKey=ULID/timestamp)    │
 │                                                                                │
 │  Async Processing                                                              │
 │    • Queue trigger (Azure Storage Queue) for SK agent messages                │
 │                                                                                │
 │  HTTP APIs                                                                     │
 │    • /messages → chat polling                                                  │
 │    • /dashboard → MCP‑UI schema                                                │
 │    • /aml/infer, /aml/train → AML control                                      │
 └──────────────────────────────────────────────────────────────────────────────┘
                ▲                                   ▲
                │                                   │
                │                                   │
 ┌─────────────────────────────────────┐   ┌────────────────────────────────────┐
 │ Azure Storage Queue                 │   │ Azure Table Storage                │
 │  • Low‑cost async message bus        │   │  • Durable chat/event store        │
 │  • Triggers host functions           │   │  • Queried by frontend polling     │
 └─────────────────────────────────────┘   └────────────────────────────────────┘
                ▲
                │
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │                  Semantic Kernel Multi‑Agents Layer                           │
 │──────────────────────────────────────────────────────────────────────────────│
 │  • Domain‑specific agents bound to AML LoRA adapters                          │
 │    – CMO Agent → Marketing LoRA                                               │
 │    – CFO Agent → Finance LoRA                                                 │
 │    – CTO Agent → Tech LoRA                                                    │
 │  • Orchestrate reasoning, tool use, and AML inference                         │
 │  • Emit messages/events to Storage Queue                                      │
 └──────────────────────────────────────────────────────────────────────────────┘
                │
                ▼
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │                      Azure Machine Learning (AML)                             │
 │──────────────────────────────────────────────────────────────────────────────│
 │  • LoRA adapters per domain (registered models)                               │
 │  • Online Endpoints (consumption, scale‑to‑zero)                              │
 │  • Training pipelines (triggered by host AML Manager)                         │
 │  • Model registry for versioning and binding to agents                        │
 └──────────────────────────────────────────────────────────────────────────────┘