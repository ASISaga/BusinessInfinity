# Boardroom Manifest Action Legend

This legend maps each numbered arrow in the composite architecture diagram  
to its corresponding **action / binding** and **manifest or MCP reference**.

| ID  | Action / Binding                  | Manifest / MCP Reference         |
|-----|------------------------------------|-----------------------------------|
| 1   | Load manifest for role/scope       | `manifest.mcpUi.load`             |
| 2   | Return UI schema JSON              | `mcpUi.schema`                    |
| 3   | Trigger action from UI             | `mcpUi.action.invoke`             |
| 4   | Governance validation              | `gov.validate`                    |
| 5   | Approval signal                    | `gov.approve`                     |
| 6   | Agent inference request            | `agent.invoke`                    |
| 7   | Call AML endpoint                  | `aml.endpoint.call`                |
| 8   | Return inference result            | `aml.result`                      |
| 9   | Deliver result to agent            | `agent.result`                    |
| 10  | Emit message/event                  | `agent.emit`                      |
| 11  | Trigger host function               | `queue.trigger`                   |
| 12  | Validate incoming message           | `gov.validate`                    |
| 13  | Persist message                     | `table.persist`                   |
| 14  | Return messages to UI               | `table.query`                     |
| 15  | Direct AML train/infer request      | `aml.control.request`             |
| 16  | Governance validation               | `gov.validate`                    |
| 17  | Approval signal                     | `gov.approve`                     |
| 18  | Run AML job                         | `aml.job.run`                     |
| 19  | Register LoRA adapter               | `aml.registry.register`           |
| 20  | Bind LoRA to agent                  | `agent.bindLoRA`                   |

---

## Usage Notes
- **IDs** correspond to arrow labels in the composite diagram.
- **Manifest / MCP Reference** values are the exact keys or tool bindings  
  expected in your manifest-driven boardroom environment.
- Governance validation (`gov.validate`) appears in both inference and training flows.
- LoRA lifecycle is explicit: training → registry → agent binding.