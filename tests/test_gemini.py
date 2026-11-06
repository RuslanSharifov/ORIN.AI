import pytest

from orin.app import build_registry
from orin.core.agent import Agent
from orin.providers.gemini import GeminiError, GeminiProvider


def test_gemini_text_only():
    def transport(payload):
        assert payload["tools"][0]["functionDeclarations"]
        return {"candidates": [{"content": {"parts": [{"text": "Salam!"}]}}]}

    provider = GeminiProvider(transport=transport)
    assert provider.ask("Salam", Agent(build_registry())) == "Salam!"


def test_gemini_tool_round_trip():
    payloads = []

    def transport(payload):
        payloads.append(payload)
        if len(payloads) == 1:
            return {
                "candidates": [
                    {"content": {"parts": [{"functionCall": {"name": "get_ram_usage", "args": {}}}]}}
                ]
            }
        assert payload["toolConfig"]["functionCallingConfig"]["mode"] == "NONE"
        response = payload["contents"][-1]["parts"][0]["functionResponse"]
        assert response["name"] == "get_ram_usage"
        assert response["response"]["ok"] is True
        assert response["response"]["result"]["total_gb"] > 0
        return {"candidates": [{"content": {"parts": [{"text": "RAM yoxlandı"}]}}]}

    provider = GeminiProvider(transport=transport)
    assert provider.ask("RAM necedir?", Agent(build_registry())) == "RAM yoxlandı"
    assert len(payloads) == 2


def test_unknown_tool_cannot_execute():
    def transport(payload):
        if len(payload["contents"]) == 1:
            return {
                "candidates": [
                    {"content": {"parts": [{"functionCall": {"name": "run_shell", "args": {}}}]}}
                ]
            }
        result = payload["contents"][-1]["parts"][0]["functionResponse"]["response"]
        assert result["ok"] is False
        return {"candidates": [{"content": {"parts": [{"text": "Blocked"}]}}]}

    assert GeminiProvider(transport=transport).ask("run", Agent(build_registry())) == "Blocked"


def test_empty_message_rejected():
    with pytest.raises(GeminiError):
        GeminiProvider(transport=lambda payload: {}).ask(" ", Agent(build_registry()))


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(GeminiError, match="GEMINI_API_KEY"):
        GeminiProvider()
