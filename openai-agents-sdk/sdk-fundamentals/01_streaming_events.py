"""
Underlying implementation of the OpenAI Agents SDK (part 1).

Demonstrates how Runner.run_streamed() returns a streaming object whose events
can be consumed with an `async for` loop. We inspect the different event types
that the SDK emits (agent updates, tool calls, tool outputs, message outputs).
"""

import asyncio

from agents import Agent, Runner, function_tool, ItemHelpers


@function_tool
def get_weather(city: str):
    print(city)
    return "30degree"


agent = Agent(
    name="Assistant Agent",
    instructions="use tools when needed to answer questions",
    tools=[get_weather],
)


async def main():
    # Runner.run_streamed() starts the agent run and immediately returns a
    # stream object. The actual work is consumed by iterating stream_events().
    stream = Runner.run_streamed(agent, input="how the weather of spain?")

    async for event in stream.stream_events():
        # raw_response_event = low-level token/delta events from the model.
        if event.type == "raw_response_event":
            continue

        # agent_updated_stream_event = the active agent changed (e.g. handoff).
        elif event.type == "agent_updated_stream_event":
            print(event)
            print("Agent updated to", event.new_agent.name)

        # run_item_stream_event = a higher-level "item" was produced.
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print(event)
                print(event.item.raw_item)
            elif event.item.type == "tool_call_output_item":
                print(event)
                print(event.item.output)
            elif event.item.type == "message_output_item":
                print(event)
                # Use ItemHelpers.text_message_output to extract the full text.
                print(ItemHelpers.text_message_output(event.item))

        print("=" * 20)


if __name__ == "__main__":
    asyncio.run(main())
