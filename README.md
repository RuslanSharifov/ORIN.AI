# ORIN.AI

**Local-first, modular personal AI assistant** for Windows. Designed to grow into
voice conversations, local memory, device control, Gemini integration, offline
Ollama support and, potentially, an open-source plugin ecosystem.

> **Status: v0.1 foundation.** This is a CLI with explicitly registered
> read-only system tools, not yet a conversational assistant.

## Quick start (Windows PowerShell)

Requires Python 3.11+.

```powershell
git clone https://github.com/RuslanSharifov/ORIN.AI.git
cd ORIN.AI
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
orin tools
orin run get_current_time
orin run get_ram_usage
orin run get_cpu_usage
pytest
```

To test changes before merge, run `git checkout feature/foundation-v0`
**before** installing the package.

## Initial guarantees

- Tools are allowlisted and cannot execute unregistered function names.
- Permission checks precede execution, with no privileges granted by default.
- The initial tools are read-only; their data comes from the actual machine.
- No API key, cloud account or model download required.
- Local runtime data and secrets are excluded via `.gitignore`.

## What is not included yet

AI models, autonomous agents, microphone streaming, SQLite memory, device
pairing, comprehensive input validation, production isolation and tool audit
logs. These require separate implementation and security reviews.

## Project map

- `src/orin/core/` — tool policy and registry
- `src/orin/tools/` — safe read-only utilities
- `src/orin/app.py` — wiring layer
- `src/orin/cli.py` — CLI entry point
- `tests/` — automated tests
- `docs/ARCHITECTURE.md` — design and roadmap

## Open-source plan

The repository is currently private. A license has intentionally **not**
been chosen yet; publication and contributor permissions need an explicit
license decision. See `CONTRIBUTING.md`.
