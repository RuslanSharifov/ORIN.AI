# ORIN.AI

**Local-first, modular personal AI assistant** for Windows, designed for future
Gemini, Ollama, memory, voice, device clients, and plugin integrations.

> **Status: v0.2 development branch.** The agent core is provider-neutral.
> The included demo provider is a keyword router, **not a real AI model**.

## Quick start (Windows, Python 3.11–3.13)

```powershell
git clone https://github.com/RuslanSharifov/ORIN.AI.git
cd ORIN.AI
git checkout feature/agent-core-v0
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
orin tools
orin run get_ram_usage
orin ask "RAM necedir?"
pytest
ruff check .
```

`orin ask` runs a complete offline tool-call demonstration: the demo
provider selects an allowlisted tool, the agent executes it, and the provider
formats the observed result.

## Project map

- `src/orin/core/` — tool registry, agent, contracts and session
- `src/orin/tools/` — read-only system utilities
- `src/orin/providers/` — provider interface and deterministic demo
- `src/orin/cli.py` — command-line interface
- `tests/` — automated tests
- `docs/ARCHITECTURE.md`, `docs/AGENT_CORE.md` — design and limits

## Security and open-source readiness

Tools are explicitly registered and permissions are checked before execution.
This is **not yet a security sandbox**. Model input validation, confirmation
flows, persistent audit logs, and plugin isolation remain planned.

The repository is private; no open-source license has been selected yet.
Do not commit secrets, local conversation data, or API keys.
