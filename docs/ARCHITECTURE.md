# ORIN.AI architecture

## Design principles
- **Local-first:** machine actions and durable memory stay local by default.
- **Provider agnostic:** Gemini, Ollama or future providers will implement adapters, not enter the core logic.
- **Deny by default:** only explicitly registered tools can be executed. Permissions are checked server-side.
- **Progressive complexity:** build the minimal working CLI before introducing services or databases.
- **Small resource footprint:** target Windows with 8 GB RAM; optional local models must be lightweight.
- **No implicit memory capture:** durable user preferences require an explicit opt-in or confirmation.
- **Open-source ready:** separation of concerns, tests, contribution guidelines and versioned contracts.

## Planned boundaries (not implemented yet)

```text
Clients (CLI / desktop / mobile / voice)
                |
            Agent API
                |
     Orchestrator + Policy Guard
       /        |         \
 AI Providers  Tool Registry  Memory Service
(Gemini/Ollama)      |         (SQLite)
                 Windows tools
```

Never allow model output to select arbitrary Python code, imports, shell strings,
SQL or file paths for execution. Validate structured tool arguments against
a schema before allowing calls from a model. The current registry provides a
small validated foundation; schema validation, audit logs, approval workflows,
device authentication and rate limiting are roadmap work, not security guarantees.

## Suggested future package boundaries

```text
src/orin/
  core/            # policies, tool contracts, orchestration
  tools/           # allowlisted device-specific actions
  providers/       # optional model adapters + capability detection
  memory/          # SQLite repository + explicit consent
  voice/           # VAD, streaming, interruption
  server/          # authenticated local API / websocket
  clients/         # future desktop/mobile integration
  plugins/         # versioned extension manifests and sandbox plans
```

Directories are added only when implementation arrives. No API service,
remote model, voice streaming, or background daemon exists in v0.1.

## Roadmap
1. Safe tool registry and system status (v0.1)
2. Tool argument schemas, authorization context, audit trail
3. SQLite memory (explicit create/read/update/delete)
4. Gemini adapter and validated function calling
5. Offline Ollama adapter and policy-aware router
6. Streaming voice / interruption; separate audio lifecycle
7. FastAPI with authenticated device clients
8. Signed plugin manifests, sandbox/isolation and third-party integrations
