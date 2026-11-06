"""Local CLI and optional real Gemini chat."""

import argparse
import json

from orin.app import build_registry
from orin.core.agent import Agent
from orin.core.registry import ToolError
from orin.core.session import run_turn
from orin.providers.demo import DemoProvider


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
    if args.command == "chat":
        from dotenv import load_dotenv

        from orin.providers.gemini import GeminiError, GeminiProvider

        load_dotenv()
        try:
            provider = GeminiProvider()
            agent = Agent(registry)
            if args.message is not None:
                print(provider.ask(args.message, agent))
                return 0
            print("ORIN Gemini chat. Exit: /exit")
            while True:
                try:
                    message = input("You> ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    return 0
                if message.casefold() in {"/exit", "exit", "quit"}:
                    return 0
                if message:
                    try:
                        print("ORIN>", provider.ask(message, agent))
                    except GeminiError as error:
                        print(f"ORIN error: {error}")
        except GeminiError as error:
            parser.exit(2, f"ORIN error: {error}\n")
        return 0
    try:
        result = registry.execute(args.tool)
    except ToolError as error:
        parser.exit(2, f"ORIN error: {error}\n")
    print(json.dumps({"tool": args.tool, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
