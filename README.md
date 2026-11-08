# ORIN.AI

Local-first modular terminal assistant with Gemini API integration and
strictly allowlisted read-only system tools. Windows is the primary platform;
Android Termux installation is experimental.

## Setup (Windows, Python 3.13)

```powershell
git fetch origin
git switch main
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
ORIN searches the current directory, then the user config, then the installed
project's `.env` file (including editable installations). Existing environment
variables take precedence. This lets `orin start` work from any directory\nwithout copying a key, provided the installed project still exists.
Do not commit either secret file.


## Android / Termux quraşdırılması

ORIN.AI-ni Android-də Termux ilə quraşdıra bilərsən. Repo **public** olduğu üçün
GitHub hesabına giriş və ya token tələb olunmur. Mobil uyğunluq hələ eksperimentaldır.

### 1. Termux-da quraşdır

Termux-u [F-Droid](https://f-droid.org/en/packages/com.termux/) üzərindən aç.
Aşağıdakı əmrləri ardıcıllıqla kopyala:

```bash
pkg update -y && pkg upgrade -y
pkg install -y git python python-pip python-psutil nano

git clone https://github.com/RuslanSharifov/ORIN.AI.git
cd ORIN.AI

python -m venv --system-site-packages .venv
source .venv/bin/activate

python -m pip install "rich>=13,<15" "python-dotenv>=1,<2"
python -m pip install --no-deps -e .
```

`python-psutil` Termux paketindən quraşdırılır. `--system-site-packages`
onu virtual mühitdə əlçatan edir, `--no-deps` isə təkrar kompilyasiyanın
qarşısını alır.

### 2. Gemini açarını əlavə et

```bash
cp .env.example .env
nano .env
```

`.env` faylındakı nümunə açarı **öz Gemini API açarınla** əvəz et:

```dotenv
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
ORIN_GEMINI_MODEL=gemini-3.1-flash-lite
```

Nano: yadda saxlamaq üçün **Ctrl+O**, Enter; çıxmaq üçün **Ctrl+X**.
Açarı heç vaxt GitHub-a göndərmə.

### 3. ORIN-i başlat

```bash
orin start
```

Termux-u sonradan yenidən açdıqda:

```bash
cd ~/ORIN.AI
source .venv/bin/activate
orin start
```

### Yeniləmə

```bash
cd ~/ORIN.AI
git pull origin main
source .venv/bin/activate
python -m pip install --no-deps -e .
orin start
```

Qeyd: Android-də bəzi CPU/RAM sistem məlumatları məhdud ola bilər.
Heç bir GitHub login, token və ya ayrıca test əmri tələb olunmur.

**Current limitation:** Interactive messages are independent Gemini requests.
Conversation history and long-term memory are not implemented yet.
Gemini may return transient service errors. No arbitrary shell execution
or plugin sandbox is included.

See `docs/GEMINI.md` for additional details.


## ORIN terminal dashboard (v0.6)

Run `orin start` from any folder after installation. The UI uses an
original compact ORIN wordmark and companion robot, responsive to mobile
Termux and Windows. Chat responses are separated by whitespace, without
per-message status panels or raw error tracebacks. Text wrapped in
`*emphasis*` or `**bold**` is highlighted; `__underlined__` is underlined,
and inline `code` is amber.

- `/status`: view request, success and error counts only when requested.
- `/help`: list commands.
- `/clear`: clear the screen manually.
- `/exit`: end the session.

Interactive terminals display a temporary `Thinking...` animation. Set
`ORIN_NO_ANIMATION=1` to disable animation. On Termux, ORIN automatically
clears older chat from the screen between requests every 8 messages (the
session stays active). To disable auto-clear run
`ORIN_AUTO_CLEAR_EVERY=0 orin start`, or change the number, e.g.
`ORIN_AUTO_CLEAR_EVERY=12 orin start`. Auto-clear is off by default on
other platforms. Gemini requests and chats continue even if Android blocks
access to `/proc/stat` or `/proc/meminfo`; the corresponding tool reports
that the metric is unavailable instead of crashing the session. Terminal
output does not expose Python exception tracebacks or private paths.
ORIN doesn't modify other programs' startup banners.
