"""ORIN command-line interface and interactive terminal chat."""

import argparse
import json
import os
from pathlib import Path

from orin.app import build_registry
from orin.core.agent import Agent
from orin.core.registry import ToolError
from orin.core.session import run_turn
from orin.providers.demo import DemoProvider


def render_reply(message: str):
    """Safely highlight model emphasis without interpreting arbitrary Rich markup."""
    import re

    from rich.text import Text

    result = Text()
    pattern = re.compile(r"(\\*\\*([^*\\n]+)\\*\\*|\\*([^*\\n]+)\\*|__([^_\\n]+)__|_([^_\\n]+)_)")
    position = 0
    for match in pattern.finditer(message):
        result.append(message[position:match.start()])
        result.append(next(part for part in match.groups()[1:] if part is not None),
                      style="bold bright_cyan on grey15")
        position = match.end()
    result.append(message[position:])
    return result


def start_terminal(provider, agent) -> int:
    """Isolated ORIN terminal layout; no screen clearing or external banner control."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    console = Console(highlight=False)
    mascot = (
        "     .-------.\n"
        "    /  o   o  \\\n"
        "   |     ^     |\n"
        "   |   \\___/   |\n"
        "    \\_________/\n"
        "      /|   |\\"
    )
    title = Text("ORIN.AI", style="bold bright_cyan")
    title.append("  |  PERSONAL AI ASSISTANT", style="dim")
    console.print(Panel(Text(mascot, style="bright_cyan"), title=title,
                        subtitle="Gemini  /help  /status  /clear  /exit",
                        border_style="cyan", expand=False))
    requests = successes = errors = 0

    def show_stats():
        console.print(
            f"[cyan]Requests: {requests}[/]   [green]Success: {successes}[/]"
            f"   [red]Errors: {errors}[/]"
        )

    show_stats()
    while True:
        try:
            message = input("YOU > ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]ORIN session closed.[/]")
            return 0
        if not message:
            continue
        command = message.casefold()
        if command in {"/exit", "exit", "quit", "/quit"}:
            console.print("[dim]ORIN session closed.[/]")
            return 0
        if command == "/help":
            console.print("[cyan]/help[/]  [cyan]/status[/]  [cyan]/clear[/]  [cyan]/exit[/]")
            continue
        if command == "/status":
            show_stats()
            continue
        if command == "/clear":
            # Only clear on explicit user request; never overwrite another program's output.
            console.clear()
            console.print("[bold cyan]ORIN.AI[/]  /help  /status  /exit")
            show_stats()
            continue
        from orin.providers.gemini import GeminiError

        requests += 1
        try:
            # Rich Status removes the temporary Thinking line when the request finishes.
            with console.status("[cyan]ORIN is thinking...[/]", spinner="dots"):
                reply = provider.ask(message, agent)
            successes += 1
            console.print(Text("ORIN > ", style="bold green") + render_reply(reply or "(No text returned.)"))
        except GeminiError as error:
            errors += 1
            console.print(Text("ORIN ! ", style="bold red") + Text(str(error), style="red"))
        console.print()
        show_stats()
        console.print()

def load_gemini_env() -> None:
    """Load credentials independent of the terminal's working directory.

    Order: existing environment > current directory > user config >
    installed project root. The latter supports editable installs.
    """
    from dotenv import load_dotenv

    candidates = (
        Path.cwd() / ".env",
        Path.home() / ".orin" / ".env",
        Path(__file__).resolve().parents[2] / ".env",
    )
    for candidate in candidates:
        if candidate.is_file():
            load_dotenv(candidate, override=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="ORIN.AI")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("tools", help="List registered tools")
    run = subcommands.add_parser("run", help="Execute one registered tool")
    run.add_argument("tool", help="Registered tool name")
    ask = subcommands.add_parser("ask", help="Offline deterministic agent demonstration")
    ask.add_argument("message", help="Question about time, RAM or CPU")
    chat = subcommands.add_parser("chat", help="Talk to real Gemini with safe tool calling")
    chat.add_argument("message", nargs="?", help="Optional single-turn message")
    subcommands.add_parser("start", help="Launch ORIN's interactive terminal UI")
    args = parser.parse_args()

    registry = build_registry()
    if args.command == "tools":
        for tool in registry.list_tools():
            print(f"{tool.name}: {tool.description}")
        return 0
    if args.command == "ask":
        outcome = run_turn(DemoProvider(), Agent(registry), args.message)
        print(outcome.text)
        return 0
    if args.command in {"chat", "start"}:
        from orin.providers.gemini import GeminiError, GeminiProvider

        load_gemini_env()
        try:
            provider = GeminiProvider()
            agent = Agent(registry)
            if args.command == "start":
                return start_terminal(provider, agent)
            if args.message is not None:
                print(provider.ask(args.message, agent))
                return 0
            return start_terminal(provider, agent)
        except GeminiError as error:
            parser.exit(2, f"ORIN error: {error}\n")
    try:
        result = registry.execute(args.tool)
    except ToolError as error:
        parser.exit(2, f"ORIN error: {error}\n")
    print(json.dumps({"tool": args.tool, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
