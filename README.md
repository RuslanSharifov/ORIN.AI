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


## Android / Termux qurulumu (experimental)

> **Status:** ORIN.AI v0.6 Termux-da real Android cihazında hələ test edilməyib.
> Gemini mətn çatının və Rich terminal UI-nin işləməsi gözlənilir. Android-də CPU/RAM
> göstəriciləri cihazın icazələrindən və `psutil` imkanlarından asılı ola bilər.
> Root, `sudo` və telefonun yaddaşına ümumi giriş icazəsi tələb olunmur.

### 1. Termux-u quraşdır

Termux-u [F-Droid](https://f-droid.org/en/packages/com.termux/) və ya
[Termux-un rəsmi GitHub releases](https://github.com/termux/termux-app/releases)
səhifəsindən quraşdır. Stabil Android paketi üçün bu mənbələr tövsiyə olunur.
Termux və onun əlavə tətbiqlərini fərqli mənbələrdən qarışdırma.
Play Store versiyasının bəzi funksiyaları fərqli ola bilər.

Açılan Termux terminalında aşağıdakı əmrləri ardıcıllıqla işlət:

```bash
pkg update && pkg upgrade -y
pkg install -y python python-pip python-psutil git gh nano
python --version
python -m pip --version
```

**Niyə `python-psutil`?** ORIN sistem məlumatları üçün `psutil` istifadə edir.
Android/Termux-da adi `pip install psutil` C-kompilyasiya xətası verə bilər.
Ona görə Termux-un paketindən istifadə edirik.

### 2. Özəl GitHub repozitoriyasını endir

`RuslanSharifov/ORIN.AI` hazırda **private** repo olduğu üçün telefonda
GitHub hesabına giriş etməlisən. Təhlükəsiz üsul: GitHub CLI-nin brauzer
autentifikasiyası (tokeni terminala, komanda sətrinə və ya README-yə yazma).

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth status
cd ~
gh repo clone RuslanSharifov/ORIN.AI
cd ORIN.AI
git switch main
```

`gh auth login` brauzerdə təsdiq/kod tələb edə bilər. Hesabın repoya giriş
hüququ olmalıdır. Repo nə vaxtsa *public* olsa, alternativ:

```bash
git clone https://github.com/RuslanSharifov/ORIN.AI.git
cd ORIN.AI
```

### 3. Python virtual mühitini və ORIN-i qur

`--system-site-packages` Termux-da sistem paketi olaraq qurduğumuz
`python-psutil` modulunu virtual mühitə görünən edir.

```bash
cd ~/ORIN.AI
python -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install "rich>=13,<15" "python-dotenv>=1,<2"
python -m pip install --no-deps -e .
```

**Vacib:** Son əmrdə `--no-deps` saxla: bu, `pip`-in Android-də
`psutil`-i yenidən kompilyasiya etməyə çalışmasının qarşısını alır.
Digər iki asılılıq əvvəlki əmrlə qurulub. Repo `pyproject.toml` faylındakı
asılılıqlar dəyişərsə bu quraşdırma üsulu yenidən nəzərdən keçirilməlidir.

Quraşdırmanı açar göstərmədən sına:

```bash
python -c "import psutil, rich, dotenv, orin; print('ORIN imports: OK')"
orin tools
orin run get_current_time
```

### 4. Gemini API açarını təhlükəsiz əlavə et

Layihə qovluğunda `.env` faylı yarat:

```bash
cd ~/ORIN.AI
nano .env
```

Fayla aşağıdakıları daxil et; `YOUR_GEMINI_API_KEY` yerinə **öz açarını**
yaz. Bu, sənəd üçün nümunədir; real açarını GitHub-a göndərmə.

```dotenv
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
ORIN_GEMINI_MODEL=gemini-3.1-flash-lite
```

`nano`-da yadda saxla: **Ctrl+O**, Enter; çıxış: **Ctrl+X**.
Sonra fayl icazəsini məhdudlaşdır:

```bash
chmod 600 ~/ORIN.AI/.env
```

`.env` Git-də nəzərə alınmır (`.gitignore`), amma yenə də onu
heç kimlə paylaşma. Modelin əlçatanlığı Gemini hesabından asılıdır.

### 5. ORIN.AI-ni işə sal

```bash
cd ~/ORIN.AI
source .venv/bin/activate
orin start
```

Əmrlər: `/help`, `/status`, `/clear`, `/exit`.
Qısa sınaq üçün başqa komandalar:

```bash
orin chat "Salam, ORIN!"
orin ask "RAM necedir?"
orin run get_cpu_usage
```

İnternet/Gemini yalnız `orin chat` və `orin start`-dakı real AI
cavabları üçün tələb olunur. `orin ask` sadə offline demo-dur.

### 6. Başqa qovluqdan istifadə və yenidən açma

`orin` əmri virtual mühit aktiv olduqda istənilən qovluqdan işləyir;
konfiqurasiya isə quraşdırılmış layihənin `.env` faylından oxunur.

```bash
source ~/ORIN.AI/.venv/bin/activate
cd ~
orin start
```

Alternativ olaraq, virtual mühiti aktivləşdirmədən birbaşa:

```bash
~/ORIN.AI/.venv/bin/orin start
```

### 7. Son yenilikləri quraşdır

```bash
cd ~/ORIN.AI
git switch main
git pull --ff-only origin main
source .venv/bin/activate
python -m pip install --no-deps -e .
orin start
```

`.env` faylı yerində qalmalıdır. Termux-un Python versiyası əsaslı
dəyişəndə `.venv` mühitinin yenidən yaradılması lazım ola bilər.

### 8. Tez-tez rast gəlinən problemlər

| Problem | Yoxlama / həll |
| --- | --- |
| `Repository not found` / `403` | `gh auth status` ilə girişini və özəl repo icazəni yoxla; `gh auth login` ilə yenidən daxil ol. |
| `No module named psutil` | `pkg install python-psutil` et, virtual mühitin `--system-site-packages` ilə yaradıldığını yoxla. |
| `Failed building wheel for psutil` | `pkg install python-psutil` və `python -m pip install --no-deps -e .` üsulunu istifadə et. |
| `pip: command not found` | `pkg install python-pip` et; virtual mühiti yenidən aktivləşdir. |
| `orin: command not found` | `source ~/ORIN.AI/.venv/bin/activate` et və `python -m pip install --no-deps -e .` əmrini təkrar işə sal. |
| `GEMINI_API_KEY is missing` | `~/ORIN.AI/.env` faylının mövcudluğunu və dəyişən adını yoxla; açarı ekrana çıxarma. |
| API `429` / `503` | Şəbəkəni, Gemini limitlərini və model əlçatanlığını yoxla; sonradan yenidən sına. |
| Banner/animasiya qarışıq görünür | Terminalı genişləndir və ya animasiyanı söndür: `ORIN_NO_ANIMATION=1 orin start`. |

İstəyə görə yalnız testləri quraşdırıb işlədə bilərsən (mobil üçün
`ruff` məcburi deyil):

```bash
source ~/ORIN.AI/.venv/bin/activate
python -m pip install pytest
python -m pytest
```

**Məhdudiyyətlər:** Bu versiya telefonun kamera, mikrofon və digər
Android icazələrini idarə etmir. Səsli idarəetmə, Android automation,
uzunmüddətli yaddaş və tam platforma uyğunluğu hələ hazırlanmayıb.

Rəsmi istinadlar:
[Termux quraşdırılması](https://github.com/termux/termux-app#installation) ·
[GitHub CLI / Android](https://github.com/cli/cli/blob/trunk/docs/install_linux.md#android) ·
[`psutil` installation](https://psutil.io/install/).

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
