"""A responsive, self-contained terminal experience for ORIN.AI.

The UI does not clear the screen on launch or alter another application's output.
"""

from __future__ import annotations

import os
import re
import sys
from contextlib import nullcontext
from dataclasses import dataclass
from time import monotonic

from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

# Original compact logo and robotic companion, designed for narrow Termux screens.
WORDMARK = (
    "  ╔═╗ ╦═╗ ╦ ╔╗╔",
    "  ║ ║ ╠╦╝ ║ ║║║",
    "  ╚═╝ ╩╚═ ╩ ╝╚╝",
)
COMPANION = (
    "     ╭─────────────╮ ",
    "  ╭──┤  ●       ●  ├──╮",
    "  │  │     ───     │  │",
    "  ╰──┤   ╰─────╯   ├──╯",
    "     ╰──────┬──────╯ ",
    "            ◆        ",
)

# Strip complete ANSI sequences, not only ESC bytes or Rich markup.
ANSI_ESCAPE = re.compile(
    r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\)|.)"
)
CONTROL_CODES = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")
EMPHASIS = re.compile(
    r"(?P<code>`[^`\n]+`)"
    r"|(?P<bold>\*\*[^*\n]+\*\*)"
    r"|(?P<under>__[^_\n]+__)"
    r"|(?P<italic>\*[^*\n]+\*|_[^_\n]+_)"
)


def render_reply(message: str) -> Text:
    """Highlight Markdown-like emphasis safely without interpreting Rich markup."""
    safe = CONTROL_CODES.sub("", ANSI_ESCAPE.sub("", message))
    result = Text(no_wrap=False)
    pos = 0
    for match in EMPHASIS.finditer(safe):
        result.append(safe[pos:match.start()])
        token = match.group(0)
        if match.lastgroup == "code":
            result.append(token[1:-1], style="bold bright_yellow on grey15")
        elif match.lastgroup == "under":
            result.append(token[2:-2], style="bold underline bright_cyan")
        elif match.lastgroup == "bold":
            result.append(token[2:-2], style="bold bright_cyan on grey15")
        else:
            result.append(token[1:-1], style="bold bright_cyan on grey15")
        pos = match.end()
    result.append(safe[pos:])
    return result


@dataclass
class SessionStats:
    requests: int = 0
    successes: int = 0
    errors: int = 0
    last_seconds: float | None = None


def _status_line(stats: SessionStats, *, compact: bool = False) -> Text:
    line = Text("  ")
    if compact:
        line.append(f"↗ {stats.requests}  ", style="bright_cyan")
        line.append(f"✓ {stats.successes}  ", style="green")
        line.append(f"! {stats.errors}", style="red")
        return line
    line.append("◉ ", style="bold bright_cyan")
    line.append(f"REQUESTS  {stats.requests:02d}  ", style="bright_white")
    line.append("✓ ", style="bold green")
    line.append(f"SUCCESS  {stats.successes:02d}  ", style="bright_white")
    line.append("! ", style="bold red")
    line.append(f"ERRORS  {stats.errors:02d}", style="bright_white")
    if stats.last_seconds is not None:
        line.append(f"   |   {stats.last_seconds:.1f}s", style="dim")
    return line


def _companion_art() -> Text:
    art = Text("\n".join(COMPANION), style="bright_cyan")
    for offset, symbol in enumerate(art.plain):
        if symbol in {"●", "◆"}:
            art.stylize("bold bright_yellow", offset, offset + 1)
    return art


def _banner(console: Console, stats: SessionStats, model: str) -> None:
    """A balanced mobile/desktop welcome screen without repeating metrics."""
    width = max(24, min(console.width, 100))
    title = Text(" ORIN.AI ", style="bold bright_cyan")
    title.append(" / personal intelligence", style="dim")
    if width >= 64:
        grid = Table.grid(expand=True, padding=(0, 2))
        grid.add_column(ratio=3)
        grid.add_column(ratio=2)
        grid.add_row(
            Group(
                Text("\n".join(WORDMARK), style="bold bright_cyan"),
                Text("     P E R S O N A L   /   A I", style="bright_white"),
                Text("     Your private workspace", style="dim"),
            ),
            Align.center(_companion_art()),
        )
        body = grid
    elif width >= 38:
        body = Group(
            Align.center(Text("\n".join(WORDMARK), style="bold bright_cyan")),
            Align.center(Text("  ◈  READY   ·   GEMINI", style="green")),
        )
    else:
        body = Align.center(Text("◈ ORIN.AI  ·  READY", style="bold bright_cyan"))
    console.print()
    console.print(
        Panel(
            body,
            title=title if width >= 38 else "ORIN.AI",
            title_align="left",
            border_style="cyan",
            padding=(1, 1) if width >= 38 else (0, 0),
            width=width,
            subtitle=Text(" /help · /status · /clear · /exit ", style="dim")
            if width >= 48
            else None,
        )
    )
    console.print()


def _show_reply(console: Console, number: int, reply: str, elapsed: float) -> None:
    """Use whitespace and a subtle heading instead of full-width answer boxes."""
    label = Text("  ◈ ORIN", style="bold bright_cyan")
    label.append(f"  ·  {elapsed:.1f}s", style="dim")
    console.print()
    console.print(label)
    console.print(Padding(render_reply(reply or "(No response text)"), (0, 1, 1, 4)))
    console.print()


def _show_error(console: Console) -> None:
    """Never display raw error text, local paths or exception tracebacks."""
    console.print()
    console.print("  [dim]◈ ORIN  ·  Sorğunu indi tamamlaya bilmədim. Yenidən yoxla.[/]")
    console.print()


def _auto_clear_frequency(console: Console) -> int:
    """Refresh clutter on small Termux screens, unless disabled by the user."""
    configured = os.getenv("ORIN_AUTO_CLEAR_EVERY")
    if configured is not None:
        try:
            return max(0, int(configured))
        except ValueError:
            return 0
    is_termux = "com.termux" in os.getenv("PREFIX", "") or bool(
        os.getenv("TERMUX_VERSION")
    )
    return 8 if is_termux else 0


def start_terminal(provider, agent, *, console: Console | None = None) -> int:
    """Run a resilient, distraction-free terminal chat on mobile and desktop."""
    console = console or Console(highlight=False)
    stats = SessionStats()
    model = str(getattr(provider, "model", "Gemini"))
    _banner(console, stats, model)
    auto_clear = _auto_clear_frequency(console)

    while True:
        try:
            console.print("[bold yellow]❯[/] [bold white]YOU[/]  ", end="")
            message = input().strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Session ended.[/]")
            return 0
        if not message:
            continue
        command = message.casefold()
        if command in {"/exit", "exit", "/quit", "quit"}:
            console.print("[dim]Session ended.[/]")
            return 0
        if command == "/help":
            console.print(
                "[dim]/help[/] commands  [dim]/status[/] metrics  "
                "[dim]/clear[/] screen  [dim]/exit[/] quit\n"
            )
            continue
        if command == "/status":
            console.print(_status_line(stats, compact=console.width < 65))
            console.print()
            continue
        if command == "/clear":
            console.clear()
            _banner(console, stats, model)
            continue

        # Refresh between requests, never in the middle of a model response.
        if auto_clear and stats.requests and stats.requests % auto_clear == 0:
            console.clear()
            console.print("[bold cyan]◈ ORIN[/]  [dim]· conversation continues[/]\n")
            clean_input = CONTROL_CODES.sub("", ANSI_ESCAPE.sub("", message))
            console.print(Text("❯ YOU  ", style="bold yellow") + Text(clean_input))

        stats.requests += 1
        started = monotonic()
        animated = (
            console.is_terminal
            and sys.stdin.isatty()
            and not os.getenv("ORIN_NO_ANIMATION")
        )
        indicator = (
            console.status("[cyan]◈ Thinking...[/]", spinner="dots", refresh_per_second=8)
            if animated
            else nullcontext()
        )
        try:
            with indicator:
                reply = provider.ask(message, agent)
        except KeyboardInterrupt:
            console.print("\n[dim]  Request interrupted.[/]\n")
            continue
        except Exception:
            # Android permissions, malformed tool outputs or network failures
            # must never terminate the interactive session or leak tracebacks.
            stats.errors += 1
            stats.last_seconds = monotonic() - started
            _show_error(console)
        else:
            stats.successes += 1
            stats.last_seconds = monotonic() - started
            _show_reply(console, stats.requests, reply, stats.last_seconds)
