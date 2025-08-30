business-infinity/
├─ server/
│  ├─ main.py
│  ├─ semantic_kernel.py
│  ├─ azure_ml.py
│  ├─ service_bus.py
│  ├─ governance.py
│  ├─ decision_engine.py
│  ├─ adapters.py
│  ├─ config_loader.py
│  └─ requirements.txt
├─ functions/
│  ├─ process_decision_event/__init__.py
│  ├─ process_decision_event/function.json
│  └─ requirements.txt
├─ mcp/
│  ├─ server.py
│  ├─ protocol.py
│  └─ requirements.txt
├─ webclient/
│  ├─ index.html
│  ├─ app.js
│  └─ styles.css
├─ configs/
│  ├─ principles.schema.json
│  ├─ decision_tree.schema.json
│  ├─ adapters.schema.json
│  ├─ principles.example.json
│  ├─ decision_tree.example.json
│  └─ adapters.example.json
├─ adapters/
│  ├─ training/
│  │  ├─ train_lora.py
│  │  ├─ aml_job.py
│  │  └─ environment.yml
│  └─ inference/
│     └─ score.py
├─ .env.example
└─ README.md