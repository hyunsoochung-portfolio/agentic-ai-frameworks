"""
Underlying implementation of the OpenAI Agents SDK (part 2).

Two ideas:
1. Consuming raw_response_event deltas to render text and tool-call arguments
   token-by-token (the basis for a real-time chat UI).
2. SQLiteSession: persistent, per-user conversation memory stored in a local
   SQLite file. Switching the session key switches the remembered context.
"""

import asyncio

from agents import Agent, Runner, function_tool, SQLiteSession


@function_tool
def get_weather(city: str):
    print(city)
    return "30degree"


agent = Agent(
    name="Assistant Agent",
    instructions="use tools when needed to answer questions",
    tools=[get_weather],
)


async def stream_deltas():
    """Render the model's output and tool-call arguments as they stream in."""
    stream = Runner.run_streamed(agent, input="how the weather of spain?")
    message = ""
    args = ""
    async for event in stream.stream_events():
        if event.type == "raw_response_event":
            event_type = event.data.type
            if event_type == "response.output_text.delta":
                message += event.data.delta
                print(message)
            elif event_type == "response.function_call_arguments.delta":
                args += event.data.delta
                print(args)
            elif event_type == "response.completed":
                message = ""
                args = ""


async def session_memory():
    """SQLiteSession gives the agent memory across turns, scoped to a user key."""
    # Each session key ("user1", "user2", ...) keeps its own history in the DB.
    session = SQLiteSession("user1", "ai-memory.db")

    await session.clear_session()
    await session.add_items([{"role": "user", "content": "my name is hyunsoo"}])

    result = await Runner.run(agent, "What is my name?", session=session)
    print(result.final_output)

    # Switching the user key means the agent cannot recall the other user's memory.
    other_session = SQLiteSession("user2", "ai-memory.db")
    result = await Runner.run(agent, "What is my name?", session=other_session)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(stream_deltas())
    asyncio.run(session_memory())
