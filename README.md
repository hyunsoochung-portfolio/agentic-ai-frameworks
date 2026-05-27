# Agentic AI Frameworks

> Hands-on practice with each major agentic-AI framework, documented as step-by-step blog walkthroughs.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI-Agents%20SDK-412991?logo=openai&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-multi--agent-1C3C3C)
![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4?logo=google&logoColor=white)

Each folder is one framework I worked through end-to-end — with its own README, dependencies, Dockerfile, and a companion walkthrough on [my blog](https://note24432.tistory.com).

| Folder | Framework | Inside |
|---|---|---|
| [`openai-agents-sdk/`](./openai-agents-sdk) | **OpenAI Agents SDK** | SDK fundamentals · a RAG / web / multimodal / MCP ChatGPT clone · a guardrailed customer-support agent |
| [`crewai/`](./crewai) | **CrewAI** | A news reader · a job-hunter agent · a multi-step content pipeline (Flows) |
| [`google-adk/`](./google-adk) | **Google Agent Development Kit** | A financial-advisor agent · a YouTube-shorts maker pipeline |
| [`foundations/`](./foundations) | **Framework-free + CrewAI starter** | A hand-coded agent loop from scratch · first steps with CrewAI |

## Why one repo

Same problems posed to four different agentic stacks. Keeping them side by side makes the trade-offs concrete instead of theoretical, and the [blog walkthroughs](https://note24432.tistory.com) accompany each folder so the next person picking up the same stack can follow the path I took.

## Getting started

Each subdirectory is independent. From inside any folder:

```bash
pip install -r requirements.txt
cp .env.example .env       # fill in API keys
# follow that folder's README for the entry point
```


---

# 📚 Full project write-ups

Every folder's full write-up is inlined below — all four framework write-ups, so you can read everything without opening a single folder. The same text lives in each project's own `README.md`.

- [OpenAI Agents SDK Projects](#openai-agents-sdk-projects)
- [CrewAI Agent Projects](#crewai-agent-projects)
- [Google ADK Agents](#google-adk-agents)
- [AI Agent Foundations](#ai-agent-foundations)


<br>

---

## OpenAI Agents SDK Projects

> 📁 [`openai-agents-sdk/`](./openai-agents-sdk)

> Three small projects I built while studying the OpenAI Agents SDK: a set of
> SDK-fundamentals scripts, a ChatGPT clone, and a multi-agent customer-support
> assistant.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI-Agents%20SDK-412991?logo=openai&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)

### Overview

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

### Projects

#### 1. SDK Fundamentals (`sdk-fundamentals/`)

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

#### 2. ChatGPT Clone (`chatgpt-clone/`)

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

#### 3. Customer Support Agent (`customer-support-agent/`)

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

### What I Learned (Technical Notes)

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

### Getting Started

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

#### Docker

```bash
docker build -t openai-agents-sdk-projects .
# Runs the ChatGPT clone on http://localhost:8501 by default.
docker run --rm -p 8501:8501 --env-file .env openai-agents-sdk-projects
# Run a different project by overriding the command, e.g.:
docker run --rm -p 8501:8501 --env-file .env openai-agents-sdk-projects \
  streamlit run customer-support-agent/main.py --server.address=0.0.0.0
```

### Notes

These are learning projects I built while studying the OpenAI Agents SDK,
following its documented patterns. The customer-support tools return mock data,
and the ChatGPT clone's File Search / MCP features need resources (a vector
store, `uvx`) set up in your own environment. No deployment, users, or metrics
are implied.


<br>

---

## CrewAI Agent Projects

> 📁 [`crewai/`](./crewai)

> A small portfolio of multi-agent applications I built while learning [CrewAI](https://github.com/crewAIInc/crewAI).

![Python](https://img.shields.io/badge/Python-3.11-blue)
![CrewAI](https://img.shields.io/badge/Framework-CrewAI-orange)
![OpenAI](https://img.shields.io/badge/LLM-OpenAI-412991)

### Overview

This repository is a set of multi-agent applications I built while learning CrewAI.
They are learning/practice projects: I worked through CrewAI's core building
blocks (Agents, Tasks, Crews) and then its event-driven **Flows**, writing one
small project at a time and reconstructing them here from my own notes and blog
posts. The goal was to understand the framework's patterns first-hand, not to
ship a product, so I've kept the code close to how I originally wrote it and
flagged any gaps honestly.

Three projects are included, in roughly increasing order of complexity:

1. **news-reader-agent** - a sequential Crew that searches the web and writes a news briefing.
2. **job-hunter-agent** - a non-linear Crew that extracts jobs, ranks them against a resume, and prepares for an interview, using Pydantic-typed outputs and a knowledge source.
3. **content-pipeline-agent** - a CrewAI **Flow** that researches a topic and generates/scores/regenerates content (tweet, blog, or LinkedIn post).

### Projects

#### 1. news-reader-agent

A sequential Crew of three agents that produces a news briefing on a topic.

- **Agents**: `news_hunter_agent` (search + scrape), `summarizer_agent` (scrape + summarize), `curator_agent` (assemble the final report).
- **Tasks** (run in order): `content_harvesting_task` -> `summarization_task` -> `final_report_assembly_task`. In a sequential Crew the output of each task is automatically passed to the next as context, so the task prompts don't need explicit `{}` parameters - they just need to state that they rely on the previous step's result.
- **Tools** (`tools.py`): `SerperDevTool` for web search and a custom `scrape_tool` that uses Playwright (headless Chromium) to load a page, then BeautifulSoup to strip non-content tags (`nav`, `footer`, `script`, ...) and return clean text.
- **Output**: each task writes a Markdown file under `output/` (`output_file` + `create_directory: true`).

Run:
```bash
cd news-reader-agent
python main.py   # kicks off with inputs={"topic": "cambodia kidnapped"}
```

#### 2. job-hunter-agent

A non-linear (DAG) Crew of five agents that turns a topic + the user's resume
into a tailored interview-prep package.

- **Agents**: `job_search_agent`, `job_matching_agent`, `resume_optimization_agent`, `company_research_agent`, `interview_prep_agent`.
- **Tasks**: `job_extraction_task` -> `job_matching_task` -> `job_selection_task`, then `resume_rewriting_task`, `company_research_task`, and finally `interview_prep_task`.
- **Typed outputs** (`models.py`): Pydantic models (`Job`, `JobList`, `RankedJob`, `RankedJobList`, `ChosenJob`) are attached to tasks via `output_pydantic=...`, which forces the LLM to return JSON that matches the schema and makes each stage's output directly consumable by the next.
- **Knowledge source**: the user's resume is loaded with `TextFileKnowledgeSource(file_paths=["resume.txt"])` from a folder that must be named `knowledge/`, and several agents are given it via `knowledge_sources=[...]`.
- **Non-linear orchestration**: instead of relying on implicit sequential passing, tasks declare their dependencies explicitly with `context=[...]`. For example, `interview_prep_task` pulls in the outputs of `job_selection_task`, `resume_rewriting_task`, and `company_research_task` - tasks that are not its immediate predecessor.
- **Tools** (`tools.py`): a `web_search_tool` built on Firecrawl (`FirecrawlApp.search(...)` with Markdown scraping), with light regex cleanup of the returned Markdown.

Run:
```bash
cd job-hunter-agent
# put your real resume in knowledge/resume.txt first
python main.py   # inputs: level / position / location
```

#### 3. content-pipeline-agent

A CrewAI **Flow** that researches a topic, generates content for a chosen
channel, scores it, and regenerates it until it passes - an event-driven,
branching workflow rather than a fixed task list.

- **Flow state** (`ContentPipelineState`, a Pydantic model): inputs (`content_type`, `topic`), internal fields (`max_length`, `research`, `score`), and the generated content (`blog_post` / `tweet` / `linkedin_post`).
- **Flow control**: `@start` -> `@listen` -> `@router`, plus the `and_` / `or_` combinators. Routers return string signals (e.g. `"make_blog"`, `"remake_tweet"`, `"check_passed"`) that other steps `@listen` for. The scoring step routes back to the matching `remake_*` handler when the score is too low, creating a self-correcting loop.
- **Structured generation**: content is produced with `LLM(model=..., response_format=SomeModel)` and parsed back with `Model.model_validate_json(...)`, which validates the JSON against the Pydantic schema.
- **Scoring crews**: `check_seo` and `check_virality` delegate to small Crews (`SeoCrew`, `ViralityCrew`) that return a `Score` (score + reason).
- `flow_basics.py` is a standalone teaching example of the Flow primitives.

Run:
```bash
cd content-pipeline-agent
python main.py        # inputs: content_type ("blog"/"tweet"/"linkedin"), topic
python flow_basics.py # the primitives demo
```

### What I Learned (Technical Notes)

These are genuine takeaways from building the projects:

- **The Agent / Task / Crew model.** An `Agent` is a role + goal + backstory (often with tools and/or knowledge); a `Task` is a description + expected output bound to an agent; a `Crew` ties a set of agents and tasks together and you run it with `kickoff(inputs=...)`. The `@CrewBase` / `@agent` / `@task` / `@crew` decorators wire YAML config (`config/agents.yaml`, `config/tasks.yaml`) to Python methods, which keeps prompts out of the code.

- **Sequential output chaining vs. explicit context.** In a plain sequential Crew, each task's output is fed to the next automatically - you don't template `{}` parameters into the prompt, you just tell the task it depends on the previous result. For non-linear workflows you instead use `context=[task_a(), task_b()]` to pull in the outputs of *specific* (not necessarily adjacent) tasks. That distinction was the main jump from project 1 to project 2.

- **Forcing structure with Pydantic.** `output_pydantic=SomeModel` on a Task (and `response_format=SomeModel` on a raw `LLM` call) makes the model emit JSON that matches a schema and raises a validation error if it doesn't. This is far more reliable than parsing free text and makes one stage's output directly usable by the next - the backbone of the job hunter.

- **Knowledge sources.** Dropping a file in a `knowledge/` folder and loading it with `TextFileKnowledgeSource` gives agents grounded, retrieval-style context (the resume, here) without baking it into every prompt.

- **Crews vs. Flows.** A Crew is essentially a task graph the framework executes for you. A **Flow** is event-driven orchestration you control: `@start` begins it, `@listen` reacts to a previous step (or to a string signal), and `@router` branches by returning a signal. With `and_` / `or_` you can fan-in/fan-out, and because state is a typed Pydantic object you can read/write it safely across steps. Flows are what let me build the regenerate-until-good-enough loop in the content pipeline, which a fixed Crew can't express cleanly.

- **Tool integration.** Tools are just decorated functions (`@tool`) returning data. I used a hosted search tool (`SerperDevTool`), a Firecrawl-based search/scrape tool, and a hand-rolled Playwright + BeautifulSoup scraper - useful for seeing the trade-off between a managed API and DIY scraping (JS rendering, tag stripping, cleanup).

### Getting Started

```bash
# 1. Clone and enter the repo
git clone https://github.com/hyunsoochung-dev/crewai-agent-projects.git
cd crewai-agent-projects

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
# news-reader-agent additionally needs the Playwright browser:
playwright install chromium

# 4. Configure your keys
cp .env.example .env
# edit .env: OPENAI_API_KEY, SERPER_API_KEY, FIRECRAWL_API_KEY

# 5. Run a project (each is self-contained; run from its own folder)
cd news-reader-agent && python main.py
# or:  cd job-hunter-agent && python main.py
# or:  cd content-pipeline-agent && python main.py
```

#### Docker

```bash
docker build -t crewai-agent-projects .

# Run a specific project by overriding the working directory:
docker run --rm --env-file .env crewai-agent-projects                       # news reader (default)
docker run --rm --env-file .env -w /app/job-hunter-agent crewai-agent-projects python main.py
docker run --rm --env-file .env -w /app/content-pipeline-agent crewai-agent-projects python main.py
```

### A Note on Completeness

These are honest learning projects, written following CrewAI's own patterns as I
worked through them. A few pieces were reconstructed best-effort from my notes:

- **news-reader-agent** `config/agents.yaml` and parts of `tasks.yaml`: my notes captured the agent/task names and key options (the `{topic}` input, `output_file` / `create_directory` / `markdown`) but not every full role/goal/backstory or description body, so those are filled in to match the intended behavior.
- **job-hunter-agent** `config/agents.yaml`: agent role/goal/backstory bodies reconstructed (the `tasks.yaml` is from the notes, with a couple of `...` truncations preserved as written).
- **content-pipeline-agent** `SeoCrew` / `ViralityCrew` (and their `config/*.yaml`): the Flow's `main.py` referenced these crews but I didn't have their source, so they're reconstructed as minimal scoring crews that return a `Score`. `Score` and the content models were also moved into a shared `models.py` to avoid a circular import.

No fabricated metrics, users, or deployments - just the code and what I learned
building it.


<br>

---

## Google ADK Agents

> 📁 [`google-adk/`](./google-adk)

> Agents I built while learning Google's Agent Development Kit (ADK).

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Google ADK](https://img.shields.io/badge/Google%20ADK-1.11%2B-4285F4?logo=google&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-google--genai-8E75B2?logo=googlegemini&logoColor=white)

### Overview

This repo collects two agents I built while learning [Google's Agent Development Kit (ADK)](https://google.github.io/adk-docs/). They are learning/practice projects: my goal was to understand how ADK structures multi-agent systems — how agents are defined, how the LLM and ADK exchange structured JSON, how session state and artifacts work, and how to wire several agents into a pipeline.

One thing I appreciated early on: with `adk web` you get a local web UI for free, so as a developer you can debug and check whether your agent logic works without building any frontend yourself.

Both agents route their LLM calls through `LiteLlm` (so the published code calls OpenAI models such as `gpt-4o`), while still using ADK's agent, tool, state, and artifact machinery.

### Projects

#### 1. Financial Advisor (`financial-advisor/`)

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

#### 2. YouTube Shorts Maker (`youtube-shorts-maker/`)

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

### What I Learned (Technical Notes)

These are my genuine takeaways from building these two projects.

- **Agent definition is declarative.** You create an `Agent` / `LlmAgent` with a `name`, `model`, `instruction`, and a list of `tools`. Tools are just Python functions — you pass the function object itself and ADK exposes it to the model. A nice surprise: ADK turns each function's signature and docstring into the JSON tool schema the LLM sees, which is why writing clear docstrings (with `Args`/`Returns`) actually matters.

- **Structured JSON communication between the LLM and ADK.** Tracing the financial advisor end to end made the loop click: ADK sends the LLM a request containing the system prompt, the conversation history, and the `tools` schemas; the LLM responds with `tool_calls` whose `arguments` are a JSON string (e.g. `{"ticker": "AAPL", "period": "1y"}`). Those argument values are *not* hard-coded in the prompt — the LLM infers them from the user input and the tool descriptions. ADK parses that JSON, runs the matching Python function, and feeds the result back as a `tool` message for the next turn.

- **Session state for sharing data between agents.** State behaves like a dict that persists for the session. A sub-agent's final text is saved automatically under its `output_key` (e.g. `state["data_analyst_result"]`), and other tools can read it later. State is only reachable through `ToolContext`.

- **`ToolContext` is injected, not constructed.** If a tool function declares `tool_context: ToolContext` as its first parameter, ADK passes it automatically; the LLM never sees or fills that parameter. That single object is the gateway to both state (`tool_context.state`) and artifacts.

- **Artifacts for persisting real files.** State holds text in memory for the session; artifacts persist binary files. You build a `types.Part(inline_data=types.Blob(mime_type=..., data=...bytes))` and call `await tool_context.save_artifact(filename, artifact)`. The financial advisor saves a Markdown report; the shorts maker saves JPEG images, MP3 audio, and the final MP4 — and later loads them back with `load_artifact` / `list_artifacts`.

- **Structured output with Pydantic.** Setting `output_schema` to a Pydantic `BaseModel` (e.g. `ContentPlanOutput`) forces the agent to return JSON matching that shape, which makes the plan safe to consume in the next stage of the pipeline.

- **Composing agents into pipelines.** Beyond a single orchestrator-with-tools, ADK provides `SequentialAgent` and `ParallelAgent`. The shorts maker runs image and voice generation in parallel, with image generation itself being a sequential prompt-builder → image-builder sub-pipeline. Wiring these together was the clearest demonstration of multi-step agent orchestration for me.

- **Callbacks can intercept a request.** A `before_model_callback` receives the `LlmRequest` and can return an `LlmResponse` to respond directly without calling the model — a simple hook point for guardrails.

### Getting Started

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

#### Docker

```bash
docker build -t google-adk-agents .
docker run --rm -p 8000:8000 --env-file .env google-adk-agents
```

The image is based on `python:3.11-slim` and installs `ffmpeg` for the video assembly step.

### Footer

These are learning projects built with Google's Agent Development Kit, following its documented patterns. They were written to understand ADK's agent definitions, structured JSON tool calling, session state, artifacts, `ToolContext`, and multi-step agent pipelines — not as production software. Some helper code (notably the Firecrawl web-search tool) is a best-effort reconstruction where the original source was not published in the posts.


<br>

---

## AI Agent Foundations

> 📁 [`foundations/`](./foundations)

> Understanding LLM agents from first principles — from a hand-coded agent loop to a first framework (CrewAI).

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?logo=openai&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-framework-FF5A50)

### Overview

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

### Projects

#### 1. From-Scratch Agent (`from-scratch-agent/`)

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

#### 2. CrewAI Setup (`crewai-setup/`)

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

### What I Learned (Technical Notes)

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

### Getting Started

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

#### Docker

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
