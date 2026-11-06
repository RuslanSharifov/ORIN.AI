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


def start_terminal(provider, agent) -> int:
    """Interactive chat with CMD-safe output (no cursor movement or spinners)."""
    print()
    print("=" * 52)
    print(" ORIN.AI  |  Personal AI Assistant")
    print(" Gemini-powered terminal workspace")
    print("=" * 52)
    print(" Commands: /help  /clear  /exit")
    print()
    while True:
        try:
            message = input("YOU> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nORIN session closed.")
            return 0
        if not message:
            continue
        command = message.casefold()
        if command in {"/exit", "exit", "quit", "/quit"}:
            print("ORIN session closed.")
            return 0
        if command == "/help":
            print("Commands: /help (help), /clear (clear screen), /exit (quit)")
            continue
        if command == "/clear":
            os.system("cls" if os.name == "nt" else "clear")
            print("ORIN.AI  |  Type /exit to quit.\n")
            continue
        from orin.providers.gemini import GeminiError

        try:
            print("ORIN> Thinking...", flush=True)
            reply = provider.ask(message, agent)
            print(f"ORIN> {reply or '(No text returned.)'}\n", flush=True)
        except GeminiError as error:
            print(f"ORIN> Error: {error}\n", flush=True)


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
