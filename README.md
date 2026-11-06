# ORIN.AI

**Local-first, modular personal AI assistant** for Windows, designed for future
Gemini, Ollama, memory, voice, device clients, and plugin integrations.

> **Status: v0.3 development branch.** The included demo provider is a
> deterministic keyword router, **not an LLM**.

## Quick start (Windows, Python 3.11–3.13)

```powershell
git clone https://github.com/RuslanSharifov/ORIN.AI.git
cd ORIN.AI
git switch feature/tool-validation-v03
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
orin tools
orin ask "RAM necedir?"
orin ask "saat necedir?"
pytest
ruff check .
```

## Architecture

- `src/orin/core/`: agent, contracts, session, tool registry and argument validation
- `src/orin/tools/`: read-only local system tools
- `src/orin/providers/`: provider protocol and offline demo
- `src/orin/cli.py`: local command line
- `tests/`: automated tests
- `docs/`: architecture, agent design, and security limitations

The registry is an allowlist, **not a sandbox**. No real LLM, Gemini API,
memory database, streaming voice or remote API is included yet.

## Open source

This repository is currently private. A license has not yet been chosen.
Never commit credentials or personal conversation history.
