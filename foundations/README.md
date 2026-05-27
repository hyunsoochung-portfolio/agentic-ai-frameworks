# AI Agent Foundations

> Understanding LLM agents from first principles — from a hand-coded agent loop to a first framework (CrewAI).

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?logo=openai&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-framework-FF5A50)

## Overview

Hands-on projects from my journey learning how LLM agents actually work, from a
hand-coded agent loop to my first framework (CrewAI). My background is in web
development, and I started studying AI agent development to explore a new area.

These are **learning / practice projects**. The goal was to first understand the
underlying mechanics of an agent by building one by hand on the raw OpenAI API
(no framework), and only then pick up a framework — so that the framework's
abstractions actually mean something instead of being magic.

Two projects:

1. **`from-scratch-agent/`** — an agent loop hard-coded on the OpenAI SDK, no framework.
2. **`crewai-setup/`** — intro to and setup of CrewAI, a multi-agent framework.

## Projects

### 1. From-Scratch Agent (`from-scratch-agent/`)

An agent loop built by hand directly on the OpenAI Chat Completions API, to see
exactly what a framework does under the hood.

- **`basic_chat.py`** — a minimal multi-turn chat loop. It keeps a running
  `messages` list so the model retains conversation context across turns. This
  is the stepping stone that shows *why* context has to be managed (the message
  list grows cumulatively).
- **`main.py`** — the full agent loop **with tool / function calling**. The model
  can either answer directly or request a tool call; the program executes the
  tool locally, feeds the result back, and calls the model again until it
  produces a final answer. This is the highlight of the project.

**Run it:**

```bash
# Multi-turn chat (no tools)
python from-scratch-agent/basic_chat.py

# Agent loop with tool calling — try "what is the weather of Spain?"
python from-scratch-agent/main.py
```

Type `q` to quit. (The `get_weather` tool is a stub that always returns
`"33 degree"` — it exists to demonstrate the loop, not to be a real weather API.)

### 2. CrewAI Setup (`crewai-setup/`)

A first crew built with [CrewAI](https://github.com/crewAIInc/crewAI), an
open-source framework for orchestrating multiple collaborating AI agents. This
project defines a small translator/counter crew using the class-based
(`@CrewBase`) pattern.

- **`config/agents.yaml`** — agent definitions (`role`, `goal`, `backstory`) for a
  `translator_agent` and a `counter_agent`.
- **`config/tasks.yaml`** — task definitions (`description`, `expected_output`,
  assigned `agent`): translate, re-translate, and count letters.
- **`tools.py`** — a custom `count_letters` tool. It's a plain Python function
  decorated with `@tool`; CrewAI reads its docstring to build the tool schema.
- **`main.py`** — assembles the `TranslatorCrew` (agents + tasks) and runs it with
  `.kickoff(inputs={"sentence": ...})`.

**Run it:**

```bash
python crewai-setup/main.py
```

The `{sentence}` placeholder in the task descriptions is filled by the `inputs`
passed to `.kickoff()`.

## What I Learned (Technical Notes)

**An "agent" is mostly a loop.** Building it by hand made this concrete. A single
API call (`client.chat.completions.create`) does not return text — it returns a
structured object, and the answer you want is `response.choices[0].message.content`.
That's just a single completion. Turning it into an agent means wrapping it in a
loop and a growing list of `messages`, where each message is a `{role, content}`
object (`user`, `assistant`, `tool`).

**Context is just a list you maintain yourself.** Multi-turn memory isn't a
feature you turn on — it's literally appending every user message and assistant
reply to `messages` and resending the whole thing each call. The obvious
consequence: the message load grows cumulatively, so a long conversation gets
large and expensive. That single observation explains a lot of what frameworks
later try to manage for you.

**The tool-calling loop has a precise shape.** The pattern I implemented:

1. Describe available tools to the model via a JSON schema (`TOOLS`), and keep a
   `FUNCTION_MAP` from tool name → the real Python callable.
2. Call the model with `messages` *and* `tools`.
3. Inspect the response. If `message.tool_calls` is empty, it's a final
   answer — done. If it's populated, the model is *requesting* a tool, not
   answering.
4. Execute the requested function. The model returns arguments as a **JSON
   string**, so you `json.loads` them into a dict before calling the function.
5. Append two things to `messages`: first the assistant's tool-call *intention*
   (`role: "assistant"` with the `tool_calls`), then the tool's result
   (`role: "tool"` with the matching `tool_call_id`).
6. Call the model again. Now it has the result and usually produces a final
   answer — i.e. the loop recurses until there are no more tool calls.

The non-obvious part was step 5: you have to record the assistant's *intention*
to call the tool back into the history, not just the result. Otherwise, on the
follow-up call the model has lost the context of what it asked and why it's
seeing that result. Pairing the assistant tool-call message with the `tool`
result message (matched by `tool_call_id`) is what keeps the conversation
coherent.

**Why frameworks abstract this.** After hand-writing the loop, CrewAI's
abstractions read as exactly the boilerplate I'd just written, named and
organized:

- **Agent** = a configured "who" (role / goal / backstory) — instead of stuffing
  persona into a system prompt by hand.
- **Task** = a "what" (description + expected output) bound to an agent — instead
  of manually prompting and parsing each step.
- **Crew** = the orchestrator that runs agents and tasks together (sequentially
  or hierarchically) and manages the message/tool plumbing I wrote by hand.

Tools become even simpler: a `@tool`-decorated function whose **docstring is the
schema** — the agent reads the docstring to decide when and how to use it. That's
the same `TOOLS` JSON schema from the from-scratch version, generated for me.
CrewAI is also designed in an OOP style: `Crew`, `Agent`, and `Task` are classes
(blueprints), and you assemble objects from them to define and run a workflow.

The overall takeaway: a framework isn't doing anything magical — it's packaging
the loop-plus-message-management that an agent fundamentally *is*, so you can
focus on roles, tasks, and collaboration instead of plumbing.

## Getting Started

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your API key(s)
cp .env.example .env
# then edit .env and set OPENAI_API_KEY=...

# 4. Run a project
python from-scratch-agent/main.py     # hand-coded agent loop with tools
# or
python crewai-setup/main.py           # CrewAI crew
```

> The original setup in the blog series used [`uv`](https://github.com/astral-sh/uv)
> (`uv init`, `uv sync`) for environment management. A standard `venv` +
> `requirements.txt` works equally well and is shown above.

### Docker

```bash
docker build -t ai-agent-foundations .

# Run the from-scratch agent (default CMD)
docker run --rm -it --env-file .env ai-agent-foundations

# Run the CrewAI project instead
docker run --rm -it --env-file .env ai-agent-foundations python crewai-setup/main.py
```

---

*Learning / practice projects built while studying these tools. The code follows
the official OpenAI SDK and CrewAI framework patterns.*
