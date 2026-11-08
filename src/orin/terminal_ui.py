"""A compact and responsive terminal experience for ORIN.AI.

Never clears the screen on startup or modifies output from other programs.
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
from rich.table import Table
from rich.text import Text

WORDMARK = (
    "  ██████╗ ██████╗ ██╗███╗   ██╗",
    " ██╔═══██╗██╔══██╗██║████╗  ██║",
    " ██║   ██║██████╔╝██║██╔██╗ ██║",
    " ██║   ██║██╔══██╗██║██║╚██╗██║",
    " ╚██████╔╝██║  ██║██║██║ ╚████║",
    "  ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝",
)

# ORIN's original pixel companion, optimized for a monospaced phone screen.
COMPANION = (
    "     ▄████████▄",
    "   ▄██        ██▄",
    "   ██  ▄█  █▄  ██",
    "   ██  ▀▀  ▀▀  ██",
    "   ▀██▄  ▄▄  ▄██▀",
    "     ▀████████▀",
    "       ▐█  █▌",
)

ANSI_CSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
CONTROL_CODES = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")
EMPHASIS = re.compile(
    r"(?P<code>\x60[^\x60\n]+\x60)"
    r"|(?P<bold>\*\*[^*\n]+\*\*)"
    r"|(?P<under>__[^_\n]+__)"
    r"|(?P<italic>\*[^*\n]+\*|_[^_\n]+_)"
)


def render_reply(message: str) -> Text:
    """Render emphasis without treating AI output as Rich markup or terminal codes."""
    safe = CONTROL_CODES.sub("", ANSI_CSI.sub("", message))
    result = Text(no_wrap=False)
    position = 0
    for match in EMPHASIS.finditer(safe):
        result.append(safe[position:match.start()])
        token = match.group(0)
        if match.lastgroup == "code":
            result.append(token[1:-1], style="bold bright_yellow on grey15")
        elif match.lastgroup == "under":
            result.append(token[2:-2], style="bold underline bright_cyan")
        elif match.lastgroup == "bold":
            result.append(token[2:-2], style="bold bright_cyan")
        else:
            result.append(token[1:-1], style="bold bright_cyan")
        position = match.end()
    result.append(safe[position:])
    return result


@dataclass
class SessionStats:
    requests: int = 0
    successes: int = 0
    errors: int = 0
    last_seconds: float | None = None


def _status_line(stats: SessionStats, *, compact: bool = False) -> Text:
    """Metrics are only shown when the user types /status."""
    line = Text()
    if compact:
        line.append(f"↗ {stats.requests}  ", style="bright_cyan")
        line.append(f"✓ {stats.successes}  ", style="green")
        line.append(f"! {stats.errors}", style="yellow")
        return line
    line.append(f"REQUESTS  {stats.requests:02d}    ", style="bright_cyan")
    line.append(f"SUCCESS  {stats.successes:02d}    ", style="green")
    line.append(f"ERRORS  {stats.errors:02d}", style="yellow")
    if stats.last_seconds is not None:
        line.append(f"    {stats.last_seconds:.1f}s", style="dim")
    return line


def _banner(console: Console, stats: SessionStats, model: str) -> None:
    """Prefer a compact phone layout and reserve full pixel typography for desktop."""
    width = max(30, min(console.width, 108))
    brand = Text(" ◈ ORIN.AI", style="bold bright_cyan")
    brand.append("   v0.6", style="dim")

    if width >= 92:
        body = Table.grid(expand=True, padding=(0, 1))
        body.add_column(ratio=3)
        body.add_column(ratio=2)
        body.add_row(
            Group(
                Text("\n".join(WORDMARK), style="bold bright_cyan"),
                Text("  P E R S O N A L   I N T E L L I G E N C E", style="white"),
            ),
            Group(
                Align.center(Text("\n".join(COMPANION), style="bright_yellow")),
                Align.center(Text("●  YOUR AI COMPANION", style="bold green")),
            ),
        )
    elif width >= 64:
        body = Table.grid(expand=True, padding=(0, 1))
        body.add_column(ratio=3)
        body.add_column(ratio=2)
        body.add_row(
            Group(
                Text("\n  O R I N", style="bold bright_cyan"),
                Text("  PERSONAL AI", style="bold white"),
                Text("\n  GEMINI  •  READY", style="bright_green"),
                Text("  /help  /status  /clear", style="dim"),
            ),
            Align.center(Text("\n".join(COMPANION), style="bright_yellow")),
        )
    elif width >= 46:
        body = Group(
            Align.center(Text("O R I N", style="bold bright_cyan")),
            Align.center(Text("\n".join(COMPANION), style="bright_yellow")),
            Align.center(Text("PERSONAL AI  •  READY", style="green")),
        )
    else:
        body = Group(
            Align.center(Text("O R I N", style="bold bright_cyan")),
            Align.center(Text("◈  PERSONAL AI", style="bright_white")),
            Align.center(Text("● READY", style="green")),
        )

    console.print()
    console.print(
        Panel(
            body,
            title=brand,
            title_align="left",
            subtitle=Text("GEMINI  •  ONLINE", style="green"),
            border_style="bright_cyan",
            padding=(1, 1),
            width=width,
        )
    )
    console.print()


def _show_reply(console: Console, number: int, reply: str, elapsed: float) -> None:
    """Display a readable, separated response without a large surrounding box."""
    console.print()
    console.print(
        Text("  ◈ ORIN", style="bold bright_cyan")
        + Text(f"  ·  {elapsed:.1f}s", style="dim")
    )
    console.print()
    message = render_reply(reply or "Cavab boş gəldi.")
    from rich.padding import Padding

    console.print(Padding(message, (0, 2)))
    console.print()


def _friendly_failure(console: Console) -> None:
    """Keep internal paths, stack traces, and secrets out of the chat transcript."""
    console.print()
    console.print(
        Text("  ◈ ORIN  ", style="bold bright_cyan")
        + Text("Sorğunu indi tamamlaya bilmədim. Yenidən cəhd et.", style="dim")
    )
    console.print()


def _auto_clear_interval(default: int = 12) -> int:
    """Refresh after a few turns on interactive terminals; 0 disables auto clearing."""
    raw = os.getenv("ORIN_AUTO_CLEAR_EVERY", str(default))
    try:
        return max(0, int(raw))
    except ValueError:
        return default


def _auto_clear_frequency(console: Console) -> int:
    """Termux screens are smaller, so refresh its conversation more often."""
    termux = "com.termux" in os.getenv("PREFIX", "")
    return _auto_clear_interval(8 if termux else 0)


def start_terminal(provider, agent, *, console: Console | None = None) -> int:
    """Run an uninterrupted chat even if an OS tool or the provider fails."""
    console = console or Console(highlight=False)
    stats = SessionStats()
    model = str(getattr(provider, "model", "Gemini"))
    _banner(console, stats, model)
    since_clear = 0

    while True:
        clear_every = _auto_clear_frequency(console)
        if console.is_terminal and clear_every and since_clear >= clear_every:
            console.clear()
            _banner(console, stats, model)
            since_clear = 0

        try:
            console.print("[bold bright_yellow]❯[/] [bold white]YOU[/]  ", end="")
            message = input().strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Session ended.[/]")
            return 0

        if not message:
            continue
        command = message.casefold()
        if command in {"/exit", "exit", "/quit", "quit"}:
            console.print("\n[dim]Session ended.[/]")
            return 0
        if command == "/help":
            console.print(
                "\n[cyan]/help[/]  [cyan]/status[/]  [cyan]/clear[/]  "
                "[cyan]/exit[/]\n"
            )
            continue
        if command == "/status":
            console.print(Panel(
                _status_line(stats, compact=console.width < 65),
                title="SESSION", border_style="cyan",
            ))
            continue
        if command == "/clear":
            console.clear()
            _banner(console, stats, model)
            since_clear = 0
            continue

        stats.requests += 1
        since_clear += 1
        started = monotonic()
        animated = (
            console.is_terminal
            and sys.stdin.isatty()
            and not os.getenv("ORIN_NO_ANIMATION")
        )
        indicator = (
            console.status(
                "[bright_cyan]◈ Thinking...[/]",
                spinner="dots", refresh_per_second=8,
            )
            if animated
            else nullcontext()
        )
        if not animated:
            console.print("[dim]  ◈ Thinking...[/]")

        try:
            with indicator:
                reply = provider.ask(message, agent)
        except Exception:
            # Android /proc restrictions, Gemini failures, etc. must not kill the chat.
            stats.errors += 1
            stats.last_seconds = monotonic() - started
            _friendly_failure(console)
        else:
            stats.successes += 1
            stats.last_seconds = monotonic() - started
            _show_reply(console, stats.requests, reply, stats.last_seconds)
