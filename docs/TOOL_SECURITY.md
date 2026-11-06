# Tool security v0.3

The registry now validates model-supplied keyword arguments against the
registered callable's Python signature. Supported parameter annotations:
`str`, `int`, `float`, and `bool`. Values are not coerced.
Unknown or missing parameters, variadic functions, unsupported annotations,
non-finite floats, long strings and excessive argument counts are rejected.

Permissions are checked **before** validation and execution.

This is a foundation, **not a security sandbox**. It does not yet enforce
value ranges (e.g. 0-100 brightness), filesystem scopes, resource timeouts,
user confirmation, process isolation, or third-party plugin isolation.
New device-mutating tools must not be exposed until those controls exist.

## Planned Gemini integration

The Gemini adapter will translate declared tool contracts into the SDK's
function declarations, disable uncontrolled automatic tool execution, and
return structured ToolCall objects for the local Agent to validate. Provider
credentials will remain server-side. The adapter is not implemented in v0.3.
