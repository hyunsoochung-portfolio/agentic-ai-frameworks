# OpenAI Agents SDK Projects

> Three small projects I built while studying the OpenAI Agents SDK: a set of
> SDK-fundamentals scripts, a ChatGPT clone, and a multi-agent customer-support
> assistant.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI-Agents%20SDK-412991?logo=openai&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)

## Overview

These are learning/practice projects I wrote while working through the OpenAI
Agents SDK. The goal was to understand the SDK's core primitives by building
something with each of them, rather than to ship a product. The code follows the
SDK's documented patterns and is honest about being practice — the
customer-support tools return mock data, for example.

The three projects build on each other in difficulty:

1. **`sdk-fundamentals/`** — small scripts that isolate one concept at a time
   (streaming events, raw token deltas, sessions, handoffs).
2. **`chatgpt-clone/`** — a Streamlit chat app that grew over a 5-part series
   into something with RAG, web search, multimodal input, image generation,
   code interpreter, and MCP servers.
3. **`customer-support-agent/`** — a multi-agent system with a triage router,
   handoffs to specialists, guardrails, tools, and a shared context object.

## Projects

### 1. SDK Fundamentals (`sdk-fundamentals/`)

Three standalone scripts exploring how the SDK works under the hood:

- **`01_streaming_events.py`** — `Runner.run_streamed()` returns a stream whose
  events are consumed with `async for`. Walks through the event types the SDK
  emits: `agent_updated_stream_event`, `run_item_stream_event` (tool calls, tool
  outputs, message outputs), and uses `ItemHelpers.text_message_output()` to pull
  the final text.
- **`02_raw_deltas_and_sessions.py`** — consumes low-level `raw_response_event`
  deltas (`response.output_text.delta`, `response.function_call_arguments.delta`)
  to render output token-by-token, and shows `SQLiteSession` giving the agent
  per-user memory backed by a local SQLite file.
- **`03_handoffs.py`** — a main agent that routes to specialist agents via
  `handoffs=[...]`, using each agent's `handoff_description`, a Pydantic
  `output_type` for structured output, and `draw_graph()` to visualize the graph.

Run any of them:

```bash
python sdk-fundamentals/01_streaming_events.py
```

### 2. ChatGPT Clone (`chatgpt-clone/`)

A Streamlit chat app (`app.py`) assembled from a 5-part series that evolved one
codebase. The final version is the most complete and combines all the
capabilities added along the way:

- **Base chat** — streaming responses + `SQLiteSession` conversation memory.
- **RAG** — `FileSearchTool` over an OpenAI vector store; uploaded `.txt` files
  are pushed into the vector store and become searchable.
- **Web search** — `WebSearchTool` for questions outside the model's training data.
- **Multimodal image input** — images are base64-encoded into a data URI and
  stored as a multimodal user message.
- **Image generation** — `ImageGenerationTool` with partial-image streaming.
- **Code interpreter** — `CodeInterpreterTool` running in an auto sandbox, with
  code rendered live as it is generated.
- **MCP servers** — a local stdio server (`MCPServerStdio` running
  `mcp-yahoo-finance` via `uvx`) and a remote hosted server (`HostedMCPTool`
  pointing at Context7 for docs).

Run it:

```bash
# Set VECTOR_STORE_ID in app.py to your own vector store id first.
streamlit run chatgpt-clone/app.py
```

> Note: the File Search tool needs a vector store you create in your own OpenAI
> account; the local MCP server needs `uv`/`uvx` available on your PATH.

### 3. Customer Support Agent (`customer-support-agent/`)

A multi-agent customer-support assistant (`main.py`, Streamlit) demonstrating the
SDK's coordination primitives:

- **Triage + handoff** — a triage agent classifies the request and hands off to
  one of four specialists (technical / billing / order / account) via
  `handoff(...)` with a structured `HandoffData` `input_type`, an `on_handoff`
  callback, and `handoff_filters.remove_all_tools` as an input filter.
- **Input guardrail** — an `@input_guardrail` runs a dedicated classifier agent
  to reject off-topic requests before the triage agent does any work.
- **Output guardrail** — the technical agent has an `@output_guardrail` that
  checks its reply doesn't leak billing/order/account content outside its role.
- **Tools** — each specialist gets its own `@function_tool` functions (mock
  diagnostics, refunds, order lookup, password resets, etc.).
- **Context** — a shared `UserAccountContext` (Pydantic) is threaded through
  every agent, tool, and guardrail via `RunContextWrapper`; dynamic instruction
  functions use it to greet the customer by name and adapt to their tier.
- **Hooks** — `AgentHooks` log tool starts/ends and handoffs into the sidebar.

Run it:

```bash
streamlit run customer-support-agent/main.py
```

## What I Learned (Technical Notes)

These are my genuine takeaways from building the three projects.

- **`Runner.run` vs `Runner.run_streamed`.** `run_streamed` returns a stream
  object immediately; the real work happens while you iterate
  `stream.stream_events()` with `async for`. That structure is what makes the
  chat UIs feel responsive — you render tokens as they arrive instead of waiting
  for the full response.
- **Two layers of events.** `raw_response_event` carries the fine-grained model
  deltas (text deltas, function-call argument deltas, tool-call progress like
  `response.web_search_call.searching`). `run_item_stream_event` is the
  higher-level "an item was produced" layer (tool call, tool output, message).
  Picking the right layer matters: I used raw deltas for live typing/code/status,
  and the item layer when I just needed the finished message.
- **Handoffs are first-class.** Instead of one mega-prompt, you give a router
  agent a list of `handoffs`, each specialist a `handoff_description`, and the
  SDK does the routing. Wrapping handoffs with `handoff(...)` lets you attach a
  structured `input_type`, an `on_handoff` callback for side effects/logging, and
  an `input_filter` (e.g. `remove_all_tools`) to clean up what the specialist
  sees. `agent_updated_stream_event` is how the UI knows a handoff happened.
- **Guardrails wrap the run, not the prompt.** An input guardrail runs before the
  agent and an output guardrail runs after; both can run their *own* sub-agent
  with a structured `output_type` to make the decision, and tripping the wire
  raises `InputGuardrailTripwireTriggered` / `OutputGuardrailTripwireTriggered`
  that you catch in the app. This cleanly separates "should we even answer" and
  "is the answer in-scope" from the main logic.
- **Tools from plain functions.** `@function_tool` turns a function's signature
  + docstring into the JSON schema the model sees — so good type hints and
  docstrings directly improve tool-calling. The first parameter receives the run
  context automatically, which is how a tool can read `context.email` or branch
  on `context.is_premium_customer()` without the model ever seeing that data.
- **Context object.** A single Pydantic `UserAccountContext` passed via
  `context=` to `Runner.run_streamed` is injected everywhere (tools, guardrails,
  dynamic instruction functions) through `RunContextWrapper`. It's a clean way to
  carry per-request state and personalize behavior across a multi-agent run.
- **Sessions = memory.** `SQLiteSession(key, db_path)` persists conversation
  history to a local file, keyed per user, so the agent remembers across turns —
  and switching the key isolates one user's memory from another's.
- **MCP integration.** A local MCP server (`MCPServerStdio`) is literally a
  subprocess you talk to over stdio, so it has to live inside an `async with`
  block; a remote one (`HostedMCPTool`) is just an HTTP endpoint described by a
  config. `cache_tools_list=True` avoids re-querying the server's tool list on
  every call. Watching the conversation log made the host ↔ LLM ↔ tool
  "ping-pong" (call → result → call → result → final answer) very concrete.

## Getting Started

```bash
# 1. Clone and enter the repo
git clone https://github.com/hyunsoochung-dev/openai-agents-sdk-projects.git
cd openai-agents-sdk-projects

# 2. Create a virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure your API key
cp .env.example .env
# then edit .env and set OPENAI_API_KEY=...

# 4. Run a project
python sdk-fundamentals/01_streaming_events.py
streamlit run chatgpt-clone/app.py
streamlit run customer-support-agent/main.py
```

### Docker

```bash
docker build -t openai-agents-sdk-projects .
# Runs the ChatGPT clone on http://localhost:8501 by default.
docker run --rm -p 8501:8501 --env-file .env openai-agents-sdk-projects
# Run a different project by overriding the command, e.g.:
docker run --rm -p 8501:8501 --env-file .env openai-agents-sdk-projects \
  streamlit run customer-support-agent/main.py --server.address=0.0.0.0
```

## Notes

These are learning projects I built while studying the OpenAI Agents SDK,
following its documented patterns. The customer-support tools return mock data,
and the ChatGPT clone's File Search / MCP features need resources (a vector
store, `uvx`) set up in your own environment. No deployment, users, or metrics
are implied.
