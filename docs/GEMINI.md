# Gemini adapter (v0.4)

Gemini uses the Google Generative Language REST `generateContent` endpoint.
`GEMINI_API_KEY` is loaded from local `.env` by the CLI; the key is sent in
an HTTP header and never committed. `ORIN_GEMINI_MODEL` defaults to
`gemini-2.5-flash`. An existing `GOOGLE_API_KEY` is also accepted.

```powershell
git fetch origin
git switch feature/gemini-v04
python -m pip install -e ".[dev]"
orin chat "Salam, ozunu tanit"
orin chat "RAM necedir?"
orin chat
```

`orin ask` remains an offline demo. `orin chat` makes real API calls.

## Safety and limitations

- Only three read-only built-in tools are exposed to Gemini.
- Gemini returns structured function calls; execution happens only in the
  local allowlisted registry, with no automatic remote code execution.
- A single bounded tool round is executed per prompt; follow-up model
  function calling is disabled.
- Interactive mode is currently **stateless**: each message is a fresh
  request. Persistent chat history and SQLite memory come later.
- Never share or commit `.env`. Cloud requests send prompts and tool results
  to Google; avoid sensitive personal data.
- A model/region/quota mismatch can cause HTTP errors. Change
  `ORIN_GEMINI_MODEL` in `.env` if your account requires a different model.
