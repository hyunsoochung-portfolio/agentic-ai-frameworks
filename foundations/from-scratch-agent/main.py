"""A hand-coded AI agent loop with tool (function) calling — no framework.

This is the "highlight" of the from-scratch series. It wires up the full
agent loop by hand on top of the raw OpenAI Chat Completions API:

    user input -> call_ai() -> the model either answers directly OR asks to
    call a tool -> we execute the tool locally -> feed the result back into
    `messages` -> call_ai() again -> the model produces a final answer.

The recursion in process_ai_response() is the loop: as long as the model
keeps returning tool_calls, we keep executing tools and calling back. When
the model returns plain content (no tool_calls), the turn is finished.

Tools are described to the model via the TOOLS schema; FUNCTION_MAP maps a
tool name back to the actual Python callable to run.
"""

import json

import openai
from openai.types.chat import ChatCompletionMessage

client = openai.OpenAI()

messages = []


# --- 1) Tool definitions ---------------------------------------------------
# TOOLS: the JSON schema the model sees (so it knows which tools exist and
# what arguments they take).
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "a function to get the weather of a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city to get the weather of",
                    }
                },
            },
        },
    }
]


def get_weather(city):
    # A stub implementation. In a real agent this would call a weather API.
    return "33 degree"


# FUNCTION_MAP: maps the tool name (as the model refers to it) to the actual
# Python function to execute.
FUNCTION_MAP = {
    "get_weather": get_weather,
}


# --- 2) The model call, with tools attached --------------------------------
def call_ai():
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
    )
    process_ai_response(response.choices[0].message)


# --- 3) Handle the model's response (the core of the loop) -----------------
def process_ai_response(message: ChatCompletionMessage):
    if message.tool_calls:
        # Record the AI's intention (the tool call) back into the history so
        # that, on the next API call, the model knows what it had requested
        # and why it is receiving these tool results.
        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in message.tool_calls
                ],
            }
        )

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = tool_call.function.arguments
            print(f"calling function: {function_name} with {arguments}")

            # The model returns arguments as a JSON string; parse to a dict
            # before calling the Python function.
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {}

            function_to_run = FUNCTION_MAP.get(function_name)
            result = function_to_run(**arguments)
            print(f"ran {function_name} with args {arguments} for a result of {result}")

            # Record the tool result so the model can use it on the next call.
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": result,
                }
            )

        # Loop back: let the model decide whether it now has enough to answer
        # (in which case the next call hits the `else` branch) or needs to
        # call another tool.
        call_ai()
    else:
        # Final response: no tool calls, so this turn is done.
        messages.append({"role": "assistant", "content": message.content})
        print(f"ai: {message.content}")


def main():
    while True:
        message = input("question to your ai agent: ")
        if message == "q":
            break
        print(f"user: {message}")
        messages.append({"role": "user", "content": message})
        call_ai()


if __name__ == "__main__":
    main()
