"""Gemini REST adapter with explicit, locally executed function calls.

Uses Gemini generateContent API. No automatic tool execution and no shell access.
"""

import json
import os
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from orin.core.agent import Agent
from orin.core.contracts import ModelResponse, ToolCall, ToolResult


class GeminiError(RuntimeError):
    """A safe, non-secret-bearing Gemini error."""


class GeminiProvider:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        *,
        transport: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key and transport is None:
            raise GeminiError("GEMINI_API_KEY is missing from .env")
        self.model = model or os.getenv("ORIN_GEMINI_MODEL", "gemini-2.5-flash")
        if not self.model.replace("-", "").replace(".", "").replace("_", "").isalnum():
            raise GeminiError("Invalid Gemini model name")
        self._transport = transport or self._request

    def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            + quote(self.model, safe="")
            + ":generateContent"
        )
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key or "",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=35) as response:
                return json.load(response)
        except HTTPError as error:
            # Never echo upstream response bodies: they may contain private details.
            raise GeminiError(f"Gemini HTTP error {error.code}; check API key/model/quota") from None
        except (URLError, TimeoutError, ValueError) as error:
            raise GeminiError("Gemini request failed or returned invalid JSON") from error

    @staticmethod
    def _parts(response: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            return response["candidates"][0]["content"]["parts"]
        except (KeyError, IndexError, TypeError) as error:
            raise GeminiError("Gemini returned no usable candidate") from error

    def ask(self, message: str, agent: Agent) -> str:
        if not message.strip() or len(message) > 12000:
            raise GeminiError("Message must be between 1 and 12000 characters")
        declarations = []
        for spec in agent.registry.list_tools():
            # v0.4 intentionally exposes ONLY built-in read-only, zero-argument tools.
            if spec.name not in {"get_current_time", "get_ram_usage", "get_cpu_usage"}:
                continue
            declarations.append(
                {
                    "name": spec.name,
                    "description": spec.description,
                    "parameters": {"type": "OBJECT", "properties": {}},
                }
            )
        contents: list[dict[str, Any]] = [
            {"role": "user", "parts": [{"text": message}]}
        ]
        payload: dict[str, Any] = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": "You are ORIN, a concise Azerbaijani personal assistant. "
                            "Use tools when needed. Never claim an action succeeded without tool results."}]
            },
            "tools": [{"functionDeclarations": declarations}],
            "toolConfig": {"functionCallingConfig": {"mode": "AUTO"}},
        }
        first_parts = self._parts(self._transport(payload))
        calls: list[ToolCall] = []
        for part in first_parts:
            if "functionCall" in part:
                call = part["functionCall"]
                if not isinstance(call.get("args", {}), dict):
                    raise GeminiError("Invalid Gemini function arguments")
                calls.append(ToolCall(name=call["name"], arguments=call.get("args", {})))
        if not calls:
            return "".join(part.get("text", "") for part in first_parts).strip()
        try:
            outcome = agent.process(ModelResponse(tool_calls=tuple(calls)))
        except ValueError as error:
            raise GeminiError("Too many tool calls requested") from error
        # Preserve the model's exact function call parts for correct conversation replay.
        contents.append({"role": "model", "parts": first_parts})
        result_parts: list[dict[str, Any]] = []
        for result in outcome.results:
            result_parts.append(
                {
                    "functionResponse": {
                        "name": result.name,
                        "response": {
                            "ok": result.ok,
                            "result": result.data if result.ok else None,
                            "error": result.error if not result.ok else None,
                        },
                    }
                }
            )
        contents.append({"role": "user", "parts": result_parts})
        payload["toolConfig"] = {"functionCallingConfig": {"mode": "NONE"}}
        final_parts = self._parts(self._transport(payload))
        return "".join(part.get("text", "") for part in final_parts).strip()
