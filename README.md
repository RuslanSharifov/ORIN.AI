# ORIN.AI

Local-first modular Windows assistant, with Gemini API integration and
strictly allowlisted read-only system tools.

## Setup (Windows, Python 3.13)

```powershell
git fetch origin
git switch feature/start-terminal-ui-v05
python -m pip install -e ".[dev]"
```

Keep your existing Gemini key in the project `.env` file:

```dotenv
GEMINI_API_KEY=your_key_here
ORIN_GEMINI_MODEL=gemini-3.1-flash-lite
```

## Launch the terminal UI

```powershell
orin start
```

A branded terminal UI appears with a persistent prompt. Type questions
normally and read responses under `ORIN>`. Built-in commands:
`/help`, `/clear`, `/exit`.

Other commands:
- `orin chat "Salam"`: one-shot Gemini request
- `orin chat`: interactive terminal UI
- `orin ask "RAM necedir?"`: offline keyword demo (no Gemini)
- `orin tools`: list registered tools
- `orin run get_ram_usage`: run a local read-only tool

## Use from anywhere on Windows

While the project's virtual environment is active, `orin start` can run
from any directory. To use the command without activating the project venv,
install the CLI in a dedicated pipx environment:

```powershell
py -m pip install --user pipx
py -m pipx ensurepath
# Open a NEW terminal after ensurepath
py -m pipx install C:\Users\User\Project\ORIN.AI
```

For a globally launched ORIN, store the API key in
`%USERPROFILE%\.orin\.env` (e.g. `C:\Users\User\.orin\.env`).
ORIN loads `.env` from the current directory first, then the user config.
Do not commit either secret file.

**Current limitation:** Interactive messages are independent Gemini requests.
Conversation history and long-term memory are not implemented yet.
Gemini may return transient service errors. No arbitrary shell execution
or plugin sandbox is included.

See `docs/GEMINI.md` for additional details.
