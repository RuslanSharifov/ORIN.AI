# ORIN.AI

Local-first modular Windows assistant, with a real Gemini integration and
strictly allowlisted system tools. Designed for future Ollama, SQLite memory,
voice, device clients and an optional open-source plugin ecosystem.

## Quick start (Windows, Python 3.13)

```powershell
git fetch origin
git switch feature/gemini-v04
python -m pip install -e ".[dev]"
```

Add your key to local `.env` (never commit it):

```dotenv
GEMINI_API_KEY=your_key_here
ORIN_GEMINI_MODEL=gemini-2.5-flash
```

```powershell
orin chat "Salam"
orin chat "RAM necedir?"
orin chat
pytest
ruff check .
```

- `orin chat`: real Gemini API, optional safe function calling
- `orin ask`: offline deterministic demo (no Gemini)
- `orin tools`: list registered tools
- `orin run get_ram_usage`: run a local read-only tool

Read `docs/GEMINI.md` for security and limitations.
The interactive Gemini chat is stateless in this version.

This repository is private and an open-source license has not been selected.
