"""A minimal offline CLI with a deterministic agent demonstration."""

import argparse
import json

from orin.app import build_registry
from orin.core.agent import Agent
from orin.core.registry import ToolError
from orin.core.session import run_turn
from orin.providers.demo import DemoProvider


def main() -> int:
    parser = argparse.ArgumentParser(description="ORIN.AI local foundation")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("tools", help="List registered tools")
    run = subcommands.add_parser("run", help="Execute one registered tool")
    run.add_argument("tool", help="Registered tool name")
    ask = subcommands.add_parser("ask", help="Offline deterministic agent demonstration")
    ask.add_argument("message", help="Question about time, RAM or CPU")
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
    try:
        result = registry.execute(args.tool)
    except ToolError as error:
        parser.exit(2, f"ORIN error: {error}\n")
    print(json.dumps({"tool": args.tool, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
