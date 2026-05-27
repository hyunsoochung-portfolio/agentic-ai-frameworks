"""
Customer support multi-agent app (OpenAI Agents SDK + Streamlit).

A triage agent applies an input guardrail, then hands off to one of four
specialist agents (technical / billing / order / account). Each specialist has
its own tools; the technical agent additionally has an output guardrail. A
shared UserAccountContext is threaded through every agent, tool, and guardrail.

Run:  streamlit run main.py
"""

import asyncio

import dotenv
import streamlit as st
from openai import OpenAI
from agents import (
    Runner,
    SQLiteSession,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
)

from models import UserAccountContext
from my_agents.triage_agent import triage_agent

dotenv.load_dotenv()

client = OpenAI()

# The context object the SDK injects into every agent/tool/guardrail this run.
user_account_ctx = UserAccountContext(
    customer_id=1,
    name="nico",
    tier="basic",
)

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "customer-support-memory.db",
    )
session = st.session_state["session"]

# Start at the triage agent; this is swapped to the active agent on handoff.
if "agent" not in st.session_state:
    st.session_state["agent"] = triage_agent


async def paint_history():
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$", "\\$"))


try:
    asyncio.run(paint_history())
except RuntimeError:
    # An event loop may already be running when Streamlit re-executes.
    pass
except Exception as e:
    st.error(f"Error loading history: {e}")


async def run_agent(message):
    with st.chat_message("ai"):
        text_placeholder = st.empty()
        response = ""
        st.session_state["text_placeholder"] = text_placeholder
        try:
            stream = Runner.run_streamed(
                st.session_state["agent"],
                message,
                session=session,
                context=user_account_ctx,
            )
            async for event in stream.stream_events():
                if event.type == "raw_response_event":
                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta
                        text_placeholder.write(response.replace("$", "\\$"))
                elif event.type == "agent_updated_stream_event":
                    # The active agent changed (a handoff happened).
                    current_name = st.session_state["agent"].name
                    if current_name != event.new_agent.name:
                        st.write(
                            f"🤖 Transfered from {current_name} to {event.new_agent.name}"
                        )
                        st.session_state["agent"] = event.new_agent
                        text_placeholder = st.empty()
                        st.session_state["text_placeholder"] = text_placeholder
                        response = ""
        except InputGuardrailTripwireTriggered:
            st.write("I can't help you with that.")
        except OutputGuardrailTripwireTriggered:
            st.write("Cant show you that answer.")
            st.session_state["text_placeholder"].empty()


message = st.chat_input("Write a message for your assistant")
if message:
    with st.chat_message("human"):
        st.write(message)
    asyncio.run(run_agent(message))


with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
