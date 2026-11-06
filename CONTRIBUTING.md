# Contributing to ORIN.AI

Thanks for your interest! Development is currently on a private repository.
We may open-source the project later; licensing will be decided before publication.

## Development
Use Python 3.11+:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
ruff check .
```

Keep changes focused, add tests for new tools, never commit credentials or
private conversation logs, and never introduce commands that run arbitrary
model-generated code. Prefer pull requests to direct pushes to main.

## Safety requirements
New capabilities must declare permissions and reject dangerous inputs.
Destructive actions will require user confirmation once supported.
