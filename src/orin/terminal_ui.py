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
from rich.table import Table
from rich.text import Text

# Original pixel wordmark and orbital droid, independent of fonts and tools.
WORDMARK = (
    "  ██████╗ ██████╗ ██╗███╗   ██╗",
    " ██╔═══██╗██╔══██╗██║████╗  ██║",
    " ██║   ██║██████╔╝██║██╔██╗ ██║",
    " ██║   ██║██╔══██╗██║██║╚██╗██║",
    " ╚██████╔╝██║  ██║██║██║ ╚████║",
    "  ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝",
)
DROID = (
    "       .--[O]--.   ",
    "     .'  o   o  '. ",
    "    /    .---.    \\",
    "   |     `---'     |",
    "    \\    _____    / ",
    "     '._[___]_. '  ",
)

# Never interpret model text as Rich markup or terminal control sequences.
CONTROL_CODES = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")
EMPHASIS = re.compile(
    r"(?P<code>`[^`\n]+`)"
    r"|(?P<bold>\*\*[^*\n]+\*\*)"
    r"|(?P<under>__[^_\n]+__)"
    r"|(?P<italic>\*[^*\n]+\*|_[^_\n]+_)"
)


def render_reply(message: str) -> Text:
    """Highlight Markdown-like emphasis safely without interpreting Rich markup."""
    safe = CONTROL_CODES.sub("", message)
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


def _banner(console: Console, stats: SessionStats, model: str) -> None:
    width = max(30, min(console.width, 110))
    console.print()
    name = Text("ORIN", style="bold bright_cyan")
    name.append("  /  AI  ", style="bold bright_white")
    name.append("  v0.6", style="dim")

    if width >= 92:
        left = Group(
            Text("\n".join(WORDMARK), style="bold bright_cyan"),
            Text("   P E R S O N A L   I N T E L L I G E N C E", style="bold bright_white"),
            Text("   Your terminal. Your assistant.", style="dim"),
        )
        right = Group(
            Align.center(Text("\n".join(DROID), style="bold bright_yellow")),
            Text("  SESSION  /  READY", style="bold bright_green"),
            Text(f"  MODEL    {model[:24]}", style="dim"),
            Text("  /help  /status  /clear  /exit", style="cyan"),
        )
        grid = Table.grid(expand=True, padding=(0, 2))
        grid.add_column(ratio=3)
        grid.add_column(ratio=2)
        grid.add_row(left, right)
        body = grid
    elif width >= 68:
        grid = Table.grid(expand=True, padding=(0, 1))
        grid.add_column(ratio=2)
        grid.add_column(ratio=1)
        grid.add_row(
            Group(
                Text("\n".join(WORDMARK), style="bold bright_cyan"),
                Text("P E R S O N A L  /  A I", style="bold white"),
            ),
            Group(
                Text("\n".join(DROID), style="bold bright_yellow"),
                Text("     ● READY", style="bold green"),
            ),
        )
        body = grid
    elif width >= 50:
        body = Group(
            Align.center(Text("\n".join(WORDMARK), style="bold bright_cyan")),
            Align.center(Text("  [O]  •  SYSTEM READY", style="bold bright_yellow")),
            Align.center(Text("/help   /status   /exit", style="cyan")),
        )
    else:
        body = Group(
            Align.center(Text("  ORIN.AI  ", style="bold bright_cyan")),
            Align.center(Text("PERSONAL INTELLIGENCE", style="bright_white")),
            Align.center(Text("/help  /status  /exit", style="yellow")),
        )

    console.print(
        Panel(
            body,
            title=name,
            title_align="left",
            border_style="bright_cyan",
            subtitle=Text("● SYSTEM READY", style="bold green"),
            subtitle_align="right",
            width=width,
            padding=(1, 1),
        )
    )
    console.print(_status_line(stats, compact=console.width < 65))
    console.print()
    console.rule("[dim]CONVERSATION[/]", style="grey35")
    console.print()


def _show_reply(console: Console, number: int, reply: str, elapsed: float) -> None:
    title = Text(f"  ORIN  /  {number:03d}  ", style="bold bright_cyan")
    subtitle = Text(f"✓ {elapsed:.1f}s ", style="green")
    console.print(
        Panel(
            render_reply(reply or "(No response text)"),
            title=title,
            subtitle=subtitle,
            border_style="cyan",
            title_align="left",
            subtitle_align="right",
            padding=(1, 2),
            expand=True,
        )
    )


def _show_error(console: Console, number: int, error: Exception) -> None:
    console.print(
        Panel(
            Text(str(error), style="bright_red"),
            title=f"  ERROR  /  {number:03d}  ",
            title_align="left",
            border_style="red",
            padding=(0, 2),
        )
    )


def start_terminal(provider, agent, *, console: Console | None = None) -> int:
    """Launch the ORIN session without modifying external terminal programs."""
    from orin.providers.gemini import GeminiError

    console = console or Console(highlight=False)
    stats = SessionStats()
    model = str(getattr(provider, "model", "Gemini"))
    _banner(console, stats, model)

    while True:
        try:
            console.print("[bold bright_yellow]❯[/] [bold bright_white]YOU[/]  ", end="")
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
                "[cyan]/help[/] Commands   [cyan]/status[/] Statistics   "
                "[cyan]/clear[/] Clear view   [cyan]/exit[/] Quit\n"
            )
            continue
        if command == "/status":
            console.print(
                Panel(
                    _status_line(stats, compact=console.width < 65),
                    title="SESSION METRICS",
                    border_style="bright_cyan",
                )
            )
            continue
        if command == "/clear":
            console.clear()
            _banner(console, stats, model)
            continue

        stats.requests += 1
        started = monotonic()
        # Avoid live cursor animation in legacy CMD or redirected output.
        animated = (
            console.is_terminal
            and sys.stdin.isatty()
            and not os.getenv("ORIN_NO_ANIMATION")
        )
        indicator = (
            console.status(
                "[bold bright_cyan]◈ ORIN is thinking...[/]",
                spinner="dots",
                refresh_per_second=8,
            )
            if animated
            else nullcontext()
        )
        if not animated:
            console.print("[dim]  ◈ Thinking...[/]")
        try:
            with indicator:
                reply = provider.ask(message, agent)
        except GeminiError as error:
            stats.errors += 1
            stats.last_seconds = monotonic() - started
            _show_error(console, stats.requests, error)
        else:
            stats.successes += 1
            stats.last_seconds = monotonic() - started
            _show_reply(console, stats.requests, reply, stats.last_seconds)
        console.print(_status_line(stats, compact=console.width < 65))
        console.print()
