"""ORIN command-line interface and interactive terminal chat."""

import argparse
import json
from pathlib import Path

from orin.app import build_registry
from orin.core.agent import Agent
from orin.core.registry import ToolError
from orin.core.session import run_turn
from orin.providers.demo import DemoProvider


def start_terminal(provider, agent) -> int:
    """Run an interactive terminal session until the user exits."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.text import Text

    console = Console()
    console.clear()
    banner = Text()
    banner.append("  ORIN.AI  ", style="bold bright_cyan")
    banner.append("  Personal AI Assistant\n", style="white")
    banner.append("  Gemini-powered terminal workspace", style="dim")
    console.print(Panel(banner, border_style="cyan", padding=(1, 2)))
    console.print("[dim]Type /exit to quit, /help for commands, /clear to clear the screen.[/dim]\n")
    while True:
        try:
            message = Prompt.ask("[bold bright_green]YOU[/bold bright_green]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]ORIN session closed.[/dim]")
            return 0
        if not message:
            continue
        command = message.casefold()
        if command in {"/exit", "exit", "quit", "/quit"}:
            console.print("[dim]ORIN session closed.[/dim]")
            return 0
        if command == "/help":
            console.print("[cyan]/help[/cyan] commands  [cyan]/clear[/cyan] clear screen  [cyan]/exit[/cyan] quit")
            continue
        if command == "/clear":
            console.clear()
            continue
        from orin.providers.gemini import GeminiError

        try:
            with console.status("[cyan]ORIN is thinking...[/cyan]", spinner="dots"):
                reply = provider.ask(message, agent)
            console.print()
            console.print("[bold bright_cyan]ORIN>[/bold bright_cyan]")
            console.print(reply or "[dim](No text returned.)[/dim]")
            console.print()
        except GeminiError as error:
            console.print(f"[red]ORIN error:[/red] {error}")


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
        from dotenv import load_dotenv

        from orin.providers.gemini import GeminiError, GeminiProvider

        # The per-user config allows launching ORIN from any working directory.
        # Local .env takes precedence over the per-user config.
        load_dotenv(Path.cwd() / ".env")
        load_dotenv(Path.home() / ".orin" / ".env")
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
