"""Custom tools for the CrewAI crew.

A tool is just a Python function decorated with @tool from crewai.tools.
The docstring matters: CrewAI uses it to build the tool's schema, so the
agent reads the docstring to understand what the tool does and how to use it.
"""

from crewai.tools import tool


@tool
def count_letters(sentence: str):
    """
    this function is to count the amount of letters in a sentence.
    the input is a sentence string.
    the output is a number.
    """
    return len(sentence)
