# CrewAI Agent Projects

> A small portfolio of multi-agent applications I built while learning [CrewAI](https://github.com/crewAIInc/crewAI).

![Python](https://img.shields.io/badge/Python-3.11-blue)
![CrewAI](https://img.shields.io/badge/Framework-CrewAI-orange)
![OpenAI](https://img.shields.io/badge/LLM-OpenAI-412991)

## Overview

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

## Projects

### 1. news-reader-agent

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

### 2. job-hunter-agent

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

### 3. content-pipeline-agent

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

## What I Learned (Technical Notes)

These are genuine takeaways from building the projects:

- **The Agent / Task / Crew model.** An `Agent` is a role + goal + backstory (often with tools and/or knowledge); a `Task` is a description + expected output bound to an agent; a `Crew` ties a set of agents and tasks together and you run it with `kickoff(inputs=...)`. The `@CrewBase` / `@agent` / `@task` / `@crew` decorators wire YAML config (`config/agents.yaml`, `config/tasks.yaml`) to Python methods, which keeps prompts out of the code.

- **Sequential output chaining vs. explicit context.** In a plain sequential Crew, each task's output is fed to the next automatically - you don't template `{}` parameters into the prompt, you just tell the task it depends on the previous result. For non-linear workflows you instead use `context=[task_a(), task_b()]` to pull in the outputs of *specific* (not necessarily adjacent) tasks. That distinction was the main jump from project 1 to project 2.

- **Forcing structure with Pydantic.** `output_pydantic=SomeModel` on a Task (and `response_format=SomeModel` on a raw `LLM` call) makes the model emit JSON that matches a schema and raises a validation error if it doesn't. This is far more reliable than parsing free text and makes one stage's output directly usable by the next - the backbone of the job hunter.

- **Knowledge sources.** Dropping a file in a `knowledge/` folder and loading it with `TextFileKnowledgeSource` gives agents grounded, retrieval-style context (the resume, here) without baking it into every prompt.

- **Crews vs. Flows.** A Crew is essentially a task graph the framework executes for you. A **Flow** is event-driven orchestration you control: `@start` begins it, `@listen` reacts to a previous step (or to a string signal), and `@router` branches by returning a signal. With `and_` / `or_` you can fan-in/fan-out, and because state is a typed Pydantic object you can read/write it safely across steps. Flows are what let me build the regenerate-until-good-enough loop in the content pipeline, which a fixed Crew can't express cleanly.

- **Tool integration.** Tools are just decorated functions (`@tool`) returning data. I used a hosted search tool (`SerperDevTool`), a Firecrawl-based search/scrape tool, and a hand-rolled Playwright + BeautifulSoup scraper - useful for seeing the trade-off between a managed API and DIY scraping (JS rendering, tag stripping, cleanup).

## Getting Started

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

### Docker

```bash
docker build -t crewai-agent-projects .

# Run a specific project by overriding the working directory:
docker run --rm --env-file .env crewai-agent-projects                       # news reader (default)
docker run --rm --env-file .env -w /app/job-hunter-agent crewai-agent-projects python main.py
docker run --rm --env-file .env -w /app/content-pipeline-agent crewai-agent-projects python main.py
```

## A Note on Completeness

These are honest learning projects, written following CrewAI's own patterns as I
worked through them. A few pieces were reconstructed best-effort from my notes:

- **news-reader-agent** `config/agents.yaml` and parts of `tasks.yaml`: my notes captured the agent/task names and key options (the `{topic}` input, `output_file` / `create_directory` / `markdown`) but not every full role/goal/backstory or description body, so those are filled in to match the intended behavior.
- **job-hunter-agent** `config/agents.yaml`: agent role/goal/backstory bodies reconstructed (the `tasks.yaml` is from the notes, with a couple of `...` truncations preserved as written).
- **content-pipeline-agent** `SeoCrew` / `ViralityCrew` (and their `config/*.yaml`): the Flow's `main.py` referenced these crews but I didn't have their source, so they're reconstructed as minimal scoring crews that return a `Score`. `Score` and the content models were also moved into a shared `models.py` to avoid a circular import.

No fabricated metrics, users, or deployments - just the code and what I learned
building it.
