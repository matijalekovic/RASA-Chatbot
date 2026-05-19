# 1PAX Chatbot QA MCP Server

This repo includes a dependency-free MCP server in `mcp_server.py` for probing the
1PAX Rasa chatbot from Codex, Claude Desktop, or any MCP-capable QA client.

It supports two transports:

- `stdio` for local MCP clients.
- `http` for Railway deployments, exposed by nginx at `/mcp`.

The server is designed for QA only. It can chat with the bot, inspect NLU parses,
read trackers, and run small workflow checks. It does not modify training data,
models, actions, or user-facing content.

## Tools

- `chatbot_health` checks Rasa status, translation health, and an optional parse probe.
- `chatbot_send_message` sends one message through the REST webhook.
- `chatbot_parse` calls `/model/parse`.
- `chatbot_get_tracker` reads `/conversations/{sender}/tracker`.
- `chatbot_run_workflow` runs a custom multi-turn test with expectations.
- `chatbot_run_regression` runs small built-in suites: `smoke`, `project_context`, `team`, `translation`, or `core`.

## Local stdio usage

Point the MCP client at the Python script:

```json
{
  "mcpServers": {
    "1pax-chatbot-qa": {
      "command": "/Users/macbookpro/Documents/RASA-Chatbot/.venv/bin/python3",
      "args": [
        "/Users/macbookpro/Documents/RASA-Chatbot/mcp_server.py",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

By default, the server talks to:

- Rasa: `http://127.0.0.1:5005`
- Translation proxy: `http://127.0.0.1:5056`

Run `./start.sh` first when using the local defaults.

## Targeting Railway from a local MCP client

Set `CHATBOT_BASE_URL` to the deployed app URL:

```json
{
  "mcpServers": {
    "1pax-chatbot-qa": {
      "command": "/Users/macbookpro/Documents/RASA-Chatbot/.venv/bin/python3",
      "args": [
        "/Users/macbookpro/Documents/RASA-Chatbot/mcp_server.py",
        "--transport",
        "stdio"
      ],
      "env": {
        "CHATBOT_BASE_URL": "https://rasa-chatbot-production-1cd0.up.railway.app"
      }
    }
  }
}
```

When `CHATBOT_BASE_URL` is set, the MCP server uses the public deployment paths:

- `/status`
- `/model/parse`
- `/webhooks/rest/webhook`
- `/conversations/{sender}/tracker`
- `/api/translate`
- `/api/translate/health`

## Railway HTTP MCP endpoint

The Docker startup script now runs the MCP server on internal port `5057`, and
nginx exposes it at:

```text
https://YOUR-RAILWAY-APP/mcp
```

Health check:

```bash
curl -sS https://YOUR-RAILWAY-APP/mcp/health
```

Raw MCP initialization probe:

```bash
curl -sS https://YOUR-RAILWAY-APP/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}'
```

List tools:

```bash
curl -sS https://YOUR-RAILWAY-APP/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

Call the smoke suite:

```bash
curl -sS https://YOUR-RAILWAY-APP/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"chatbot_run_regression","arguments":{"suite":"smoke"}}}'
```

## Optional HTTP bearer token

For public Railway QA, set:

```text
MCP_BEARER_TOKEN=your-long-random-token
```

Then HTTP clients must send:

```text
Authorization: Bearer your-long-random-token
```

Local stdio clients do not need this token.

## Environment variables

- `MCP_TRANSPORT`: `stdio` or `http`. Defaults to `stdio`.
- `MCP_HOST`: HTTP bind host. Defaults to `127.0.0.1`.
- `MCP_PORT`: HTTP bind port. Defaults to `5057`.
- `MCP_BEARER_TOKEN`: optional HTTP auth token.
- `CHATBOT_BASE_URL`: public chatbot URL. Useful for local MCP clients targeting Railway.
- `RASA_BASE_URL`: direct Rasa API URL when `CHATBOT_BASE_URL` is not set.
- `TRANSLATE_BASE_URL`: direct translation proxy URL when `CHATBOT_BASE_URL` is not set.
- `MCP_CHATBOT_TIMEOUT_SECONDS`: backend request timeout. Defaults to `20`.
- `MCP_ALLOW_BASE_URL_OVERRIDE`: set to `1` to allow per-tool `base_url` overrides in trusted QA environments.

## Example workflow call

```json
{
  "name": "chatbot_run_workflow",
  "arguments": {
    "steps": [
      {
        "message": "Tell me about Bordeaux Airport",
        "expect_response_contains_any": ["Bordeaux", "airport"]
      },
      {
        "message": "How much did it cost?",
        "expect_response_contains_any": ["cost", "budget", "EUR", "Not available"]
      }
    ]
  }
}
```

The workflow tool keeps one sender id across all steps, so it is suitable for
checking project and person slot continuity.
