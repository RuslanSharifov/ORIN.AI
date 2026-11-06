# Agent core v0.2

The provider returns a `ModelResponse` containing text and zero or more
`ToolCall` values. The agent checks the allowlist and permissions in
`ToolRegistry`, then returns structured `ToolResult` values. The provider
can compose a final natural-language response from the actual results.

```text
User -> AIProvider -> ModelResponse(tool_calls)
                         |
                      Agent -> ToolRegistry -> read-only tools
                         |
                      ToolResult -> AIProvider -> final text
```

## Current limitations

- `DemoProvider` is a deterministic keyword router, **not Gemini or an LLM**.
- The current registry does not yet validate full JSON schemas, apply timeouts,
  isolate plugins, or persist an audit trail.
- Only one execution round is allowed; additional tool calls in the final
  provider response are ignored. Max calls per round: 5 by default.
- Tools are read-only, and permissions default to none.
- No conversation memory or API key is needed.

## Next

Implement strict typed JSON schemas and permission contexts before enabling
Gemini function calling or untrusted third-party plugin packages.
