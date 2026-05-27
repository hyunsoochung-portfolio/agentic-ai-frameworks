# Google ADK Agents

> Agents I built while learning Google's Agent Development Kit (ADK).

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Google ADK](https://img.shields.io/badge/Google%20ADK-1.11%2B-4285F4?logo=google&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-google--genai-8E75B2?logo=googlegemini&logoColor=white)

## Overview

This repo collects two agents I built while learning [Google's Agent Development Kit (ADK)](https://google.github.io/adk-docs/). They are learning/practice projects: my goal was to understand how ADK structures multi-agent systems — how agents are defined, how the LLM and ADK exchange structured JSON, how session state and artifacts work, and how to wire several agents into a pipeline.

One thing I appreciated early on: with `adk web` you get a local web UI for free, so as a developer you can debug and check whether your agent logic works without building any frontend yourself.

Both agents route their LLM calls through `LiteLlm` (so the published code calls OpenAI models such as `gpt-4o`), while still using ADK's agent, tool, state, and artifact machinery.

## Projects

### 1. Financial Advisor (`financial-advisor/`)

A multi-agent financial advisory system. A main `FinancialAdvisor` agent orchestrates three specialized sub-agents and one direct tool:

```
Financial Advisor (main agent)
├── Data Analyst        — company info, pricing, financial metrics (yfinance)
├── Financial Analyst   — income statement, balance sheet, cash flow (yfinance)
├── News Analyst        — current news via web search (Firecrawl)
└── save_advice_report  — writes the final report as a Markdown artifact
```

The advisor first asks the user about their investment goals, risk tolerance, and time horizon, then calls the sub-agents to gather data, and finally produces a BUY/SELL/HOLD recommendation. Each sub-agent stores its result in session state via `output_key`, and the report tool reads those values back from state.

**Run it:**

```bash
cd financial-advisor
# from the financial-advisor folder, point adk at the package
adk web
```

Then open the local URL ADK prints and select the `financial_advisor` agent.

> Note on `news_analyst` / Firecrawl: the blog posts reference a `web_search_tool` (Firecrawl) used by the News Analyst, but the exact source for that helper was not published. `financial_advisor/tools.py` is a best-effort reconstruction following Firecrawl's documented search API so the agent can run end to end.

### 2. YouTube Shorts Maker (`youtube-shorts-maker/`)

A pipeline that turns a topic into a vertical (9:16) YouTube Short. A top-level `ShortsProducerAgent` orchestrates the stages, and the pipeline mixes several ADK agent types:

```
ShortsProducerAgent (orchestrator)
├── ContentPlannerAgent          — LLM agent with a Pydantic output_schema (structured JSON plan)
├── AssetGeneratorAgent          — ParallelAgent
│   ├── ImageGeneratorAgent      — SequentialAgent
│   │   ├── PromptBuilderAgent   — builds optimized image prompts (Pydantic schema)
│   │   └── ImageBuilder         — OpenAI gpt-image-1 → saves image artifacts
│   └── VoiceGeneratorAgent      — OpenAI TTS (gpt-4o-mini-tts) → saves audio artifacts
└── VideoAssemblerAgent          — loads artifacts, runs FFmpeg → final MP4 artifact
```

It plans 3-6 scenes (max ~20s total), generates an image and narration per scene in parallel, then stitches everything together with FFmpeg into a 1080x1920 MP4. The orchestrator also demonstrates a `before_model_callback` that can short-circuit a request before it reaches the model.

**Run it:**

```bash
cd youtube-shorts-maker
adk web
```

Requires `ffmpeg` to be installed for the video assembly step (the provided Dockerfile installs it).

## What I Learned (Technical Notes)

These are my genuine takeaways from building these two projects.

- **Agent definition is declarative.** You create an `Agent` / `LlmAgent` with a `name`, `model`, `instruction`, and a list of `tools`. Tools are just Python functions — you pass the function object itself and ADK exposes it to the model. A nice surprise: ADK turns each function's signature and docstring into the JSON tool schema the LLM sees, which is why writing clear docstrings (with `Args`/`Returns`) actually matters.

- **Structured JSON communication between the LLM and ADK.** Tracing the financial advisor end to end made the loop click: ADK sends the LLM a request containing the system prompt, the conversation history, and the `tools` schemas; the LLM responds with `tool_calls` whose `arguments` are a JSON string (e.g. `{"ticker": "AAPL", "period": "1y"}`). Those argument values are *not* hard-coded in the prompt — the LLM infers them from the user input and the tool descriptions. ADK parses that JSON, runs the matching Python function, and feeds the result back as a `tool` message for the next turn.

- **Session state for sharing data between agents.** State behaves like a dict that persists for the session. A sub-agent's final text is saved automatically under its `output_key` (e.g. `state["data_analyst_result"]`), and other tools can read it later. State is only reachable through `ToolContext`.

- **`ToolContext` is injected, not constructed.** If a tool function declares `tool_context: ToolContext` as its first parameter, ADK passes it automatically; the LLM never sees or fills that parameter. That single object is the gateway to both state (`tool_context.state`) and artifacts.

- **Artifacts for persisting real files.** State holds text in memory for the session; artifacts persist binary files. You build a `types.Part(inline_data=types.Blob(mime_type=..., data=...bytes))` and call `await tool_context.save_artifact(filename, artifact)`. The financial advisor saves a Markdown report; the shorts maker saves JPEG images, MP3 audio, and the final MP4 — and later loads them back with `load_artifact` / `list_artifacts`.

- **Structured output with Pydantic.** Setting `output_schema` to a Pydantic `BaseModel` (e.g. `ContentPlanOutput`) forces the agent to return JSON matching that shape, which makes the plan safe to consume in the next stage of the pipeline.

- **Composing agents into pipelines.** Beyond a single orchestrator-with-tools, ADK provides `SequentialAgent` and `ParallelAgent`. The shorts maker runs image and voice generation in parallel, with image generation itself being a sequential prompt-builder → image-builder sub-pipeline. Wiring these together was the clearest demonstration of multi-step agent orchestration for me.

- **Callbacks can intercept a request.** A `before_model_callback` receives the `LlmRequest` and can return an `LlmResponse` to respond directly without calling the model — a simple hook point for guardrails.

## Getting Started

```bash
# 1. Clone and enter the repo
git clone https://github.com/hyunsoochung-dev/google-adk-agents.git
cd google-adk-agents

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# edit .env and fill in the keys you need (OPENAI_API_KEY at minimum;
# FIRECRAWL_API_KEY for the financial advisor's news search)

# 5. Run an agent (pick a project folder, then launch the ADK web UI)
cd financial-advisor && adk web
# or
cd youtube-shorts-maker && adk web
```

> The YouTube shorts maker also needs `ffmpeg` available on your PATH.

### Docker

```bash
docker build -t google-adk-agents .
docker run --rm -p 8000:8000 --env-file .env google-adk-agents
```

The image is based on `python:3.11-slim` and installs `ffmpeg` for the video assembly step.

## Footer

These are learning projects built with Google's Agent Development Kit, following its documented patterns. They were written to understand ADK's agent definitions, structured JSON tool calling, session state, artifacts, `ToolContext`, and multi-step agent pipelines — not as production software. Some helper code (notably the Firecrawl web-search tool) is a best-effort reconstruction where the original source was not published in the posts.
