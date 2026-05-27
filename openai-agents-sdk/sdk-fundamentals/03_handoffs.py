"""
Underlying implementation of the OpenAI Agents SDK (part 3).

Handoffs: a top-level agent routes a question to a specialist agent. Each
specialist's `handoff_description` tells the main agent what it is good for.
We also use a Pydantic `output_type` to get structured output, and draw_graph
to visualize the agent topology.
"""

import asyncio

from pydantic import BaseModel
from agents import Agent, Runner, function_tool, SQLiteSession
from agents.extensions.visualization import draw_graph


@function_tool
def get_weather(city: str):
    print(city)
    return "30degree"


class Answer(BaseModel):
    answer: str
    background_explanation: str


geography_agent = Agent(
    name="Geo Expert Agent",
    instructions="You are an expert in geography, you answer questions related to them.",
    handoff_description="Use this to answer geography related questions like city",
    tools=[get_weather],
    output_type=Answer,
)

economics_agent = Agent(
    name="Economics Expert Agent",
    instructions="You are an expert in economics, you answer questions related to them.",
    handoff_description="Use this to answer economics questions.",
)

main_agent = Agent(
    name="Main Agent",
    instructions=(
        "You are a user facing agent. You MUST transfer to the appropriate "
        "specialist agent for each question. Do not answer questions yourself - "
        "always handoff to the specialist agent. For geography questions, handoff "
        "to Geography Agent. For economy questions, handoff to Economy Agent."
    ),
    handoffs=[
        economics_agent,
        geography_agent,
    ],
)


async def main():
    session = SQLiteSession("user1", "ai-memory.db")
    result = await Runner.run(
        main_agent,
        "what is the capital of korea?",
        session=session,
    )
    # last_agent shows which specialist actually handled the request.
    print(result.last_agent.name)
    print(result.final_output)

    # Visualize the handoff graph (writes/opens a graphviz render).
    draw_graph(main_agent)


if __name__ == "__main__":
    asyncio.run(main())
