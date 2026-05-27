"""
ChatGPT clone built with the OpenAI Agents SDK + Streamlit.

This is the most complete version assembled across the blog series, which
evolved a single codebase step by step:

  Part 1  base chat: streaming responses + SQLiteSession memory
  Part 2  RAG (FileSearchTool over a vector store) + WebSearchTool + file upload
  Part 3  multimodal image input (base64) + ImageGenerationTool
  Part 4  CodeInterpreterTool (live code rendering)
  Part 5  MCP servers: a local stdio server (Yahoo Finance) and a remote
          HostedMCPTool (Context7 docs)

Because the MCP stdio server must be opened inside an async context manager,
the Agent is constructed inside run_agent() (per part 5).

Run:  streamlit run app.py
"""

import asyncio
import base64

import dotenv
import streamlit as st
from openai import OpenAI
from agents import (
    Agent,
    Runner,
    SQLiteSession,
    WebSearchTool,
    FileSearchTool,
    CodeInterpreterTool,
    ImageGenerationTool,
    HostedMCPTool,
)
from agents.mcp.server import MCPServerStdio

dotenv.load_dotenv()

client = OpenAI()

# Vector store backing the File Search (RAG) tool. Create one in the OpenAI
# dashboard / API and paste its id here.
VECTOR_STORE_ID = "vs_xxxxxxxxxxxxxxxxxxxxxxxxxx"

INSTRUCTIONS = """
You are a helpful assistant.
You have access to the following tools:
    - Web Search Tool: Use this when the user asks a question that isn't in your
      training data. Use this tool when the user asks about current or future
      events, or when you don't know the answer; try searching the web first.
    - File Search Tool: Use this tool when the user asks a question about facts
      related to themselves, or about specific files they uploaded.
    - Code Interpreter Tool: Use this tool when you need to write and run code
      to answer the user's question.
    - Image Generation Tool: Use this tool when the user requests an image to be
      generated based on a text description.
"""

# Conversation memory persisted to a local SQLite file.
if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "chat-gpt-clone-memory.db",
    )
session = st.session_state["session"]


async def paint_history():
    """Re-render past messages (Streamlit re-runs the whole script on input)."""
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    content = message["content"]
                    if isinstance(content, str):
                        st.write(content)
                    elif isinstance(content, list):
                        # Multimodal user turn (e.g. an uploaded image).
                        for part in content:
                            if "image_url" in part:
                                st.image(part["image_url"])
                else:
                    if message["type"] == "message":
                        # Escape '$' so Streamlit doesn't treat it as LaTeX.
                        st.write(message["content"][0]["text"].replace("$", "\\$"))

        if "type" in message:
            message_type = message["type"]
            if message_type == "web_search_call":
                with st.chat_message("ai"):
                    st.write("🔍 Searched the web")
            elif message_type == "file_search_call":
                with st.chat_message("ai"):
                    st.write("🗂️ Searched your files")
            elif message_type == "code_interpreter_call":
                with st.chat_message("ai"):
                    st.code(message["code"])
            elif message_type == "image_generation_call":
                image = base64.b64decode(message["result"])
                with st.chat_message("ai"):
                    st.image(image)


asyncio.run(paint_history())


def update_status(status_container, event):
    """Map a raw streaming event type to a friendly status label."""
    status_messages = {
        "response.web_search_call.completed": ("✅ Web search completed.", "complete"),
        "response.web_search_call.in_progress": ("🔍 Starting web search...", "running"),
        "response.web_search_call.searching": ("🔍 Web search in progress...", "running"),
        "response.file_search_call.completed": ("✅ File search completed.", "complete"),
        "response.file_search_call.in_progress": ("🗂️ Starting file search...", "running"),
        "response.file_search_call.searching": ("🗂️ File search in progress...", "running"),
        "response.code_interpreter_call_code.done": ("🤖 Ran code.", "complete"),
        "response.code_interpreter_call.completed": ("🤖 Ran code.", "complete"),
        "response.code_interpreter_call.in_progress": ("🤖 Running code...", "running"),
        "response.code_interpreter_call.interpreting": ("🤖 Running code...", "running"),
        "response.image_generation_call.generating": ("🎨 Drawing image...", "running"),
        "response.image_generation_call.in_progress": ("🎨 Drawing image...", "running"),
        "response.completed": (" ", "complete"),
    }
    if event in status_messages:
        label, state = status_messages[event]
        status_container.update(label=label, state=state)


async def run_agent(message):
    # The MCP stdio server is launched as a subprocess and must live inside an
    # async context manager for the duration of the run.
    yfinance_server = MCPServerStdio(
        params={
            "command": "uvx",
            "args": ["mcp-yahoo-finance"],
        },
        # Cache the tool list so we don't re-query the server on every call.
        cache_tools_list=True,
    )
    async with yfinance_server:
        agent = Agent(
            name="ChatGPT Clone",
            model="gpt-4o-mini",
            instructions=INSTRUCTIONS,
            mcp_servers=[
                yfinance_server,
            ],
            tools=[
                WebSearchTool(),
                FileSearchTool(
                    vector_store_ids=[VECTOR_STORE_ID],
                    max_num_results=3,
                ),
                CodeInterpreterTool(
                    tool_config={
                        "type": "code_interpreter",
                        "container": {
                            "type": "auto",
                        },
                    }
                ),
                ImageGenerationTool(
                    tool_config={
                        "type": "image_generation",
                        "quality": "high",
                        "output_format": "jpeg",
                        "partial_images": 1,
                    }
                ),
                # Remote MCP server (hosted) for documentation lookups.
                HostedMCPTool(
                    tool_config={
                        "server_url": "https://mcp.context7.com/mcp",
                        "type": "mcp",
                        "server_label": "Context7",
                        "server_description": "Use this to get the docs from software projects.",
                        "require_approval": "never",
                    }
                ),
            ],
        )

        with st.chat_message("ai"):
            status_container = st.status("⏳", expanded=False)
            code_placeholder = st.empty()
            image_placeholder = st.empty()
            text_placeholder = st.empty()
            response = ""
            code_response = ""
            st.session_state["code_placeholder"] = code_placeholder
            st.session_state["text_placeholder"] = text_placeholder

            stream = Runner.run_streamed(
                agent,
                message,
                session=session,
            )
            async for event in stream.stream_events():
                if event.type == "raw_response_event":
                    update_status(status_container, event.data.type)

                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta
                        text_placeholder.write(response.replace("$", "\\$"))

                    elif event.data.type == "response.code_interpreter_call_code.delta":
                        code_response += event.data.delta
                        code_placeholder.code(code_response)

                    elif event.data.type == "response.image_generation_call.partial_image":
                        image = base64.b64decode(event.data.partial_image_b64)
                        image_placeholder.image(image)

                    elif event.data.type == "response.completed":
                        image_placeholder.empty()


prompt = st.chat_input(
    "Write a message or attach an image/file for your assistant",
    accept_file=True,
    file_type=["txt", "jpg", "jpeg", "png"],
)

if prompt:
    # Clear stale placeholders from a previous run.
    if "code_placeholder" in st.session_state:
        st.session_state["code_placeholder"].empty()
    if "text_placeholder" in st.session_state:
        st.session_state["text_placeholder"].empty()

    for file in prompt.files:
        # Text files are uploaded to the vector store (RAG / File Search).
        if file.type.startswith("text/"):
            with st.chat_message("ai"):
                with st.status("⏳ Uploading file...") as status:
                    uploaded_file = client.files.create(
                        file=(file.name, file.getvalue()),
                        purpose="user_data",
                    )
                    status.update(label="⏳ Attaching file...")
                    client.vector_stores.files.create(
                        vector_store_id=VECTOR_STORE_ID,
                        file_id=uploaded_file.id,
                    )
                    status.update(label="✅ File uploaded", state="complete")

        # Images are encoded as a base64 data URI and stored directly in the
        # session as a multimodal user message (no intermediate tool call).
        elif file.type.startswith("image/"):
            with st.status("⏳ Uploading image...") as status:
                file_bytes = file.getvalue()
                base64_data = base64.b64encode(file_bytes).decode("utf-8")
                data_uri = f"data:{file.type};base64,{base64_data}"
                asyncio.run(
                    session.add_items(
                        [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "input_image",
                                        "detail": "auto",
                                        "image_url": data_uri,
                                    }
                                ],
                            }
                        ]
                    )
                )
                status.update(label="✅ Image uploaded", state="complete")
            with st.chat_message("human"):
                st.image(data_uri)

    if prompt.text:
        with st.chat_message("human"):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))


with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    # Debug: show the raw session contents.
    st.write(asyncio.run(session.get_items()))
