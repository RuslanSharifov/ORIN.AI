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

Run `orin start` from any folder after installation. The new terminal screen
uses a responsive original ORIN wordmark and droid, a live session summary and
colored user/assistant/error output. Text wrapped in `*emphasis*` or
`**bold**` is highlighted in cyan; `__underlined__` is underlined and inline
`code` is amber. Content is treated as untrusted: Rich markup and terminal
control codes in model responses cannot change the terminal.

- `/status`: show sent requests, successful answers, failures.
- `/help`: list commands.
- `/clear`: clear the terminal only when explicitly requested.
- `/exit`: end the session.

The `Thinking...` animation disappears after each request in interactive
terminals. Set `ORIN_NO_ANIMATION=1` for a static progress message. The
dashboard doesn't change other programs or suppress their startup banners.
For the full wordmark and mascot side-by-side, use a terminal at least 68
columns wide; at 92+ columns an expanded dashboard appears.
