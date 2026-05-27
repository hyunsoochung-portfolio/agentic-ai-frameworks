"""First steps with CrewAI: a class-based crew of collaborating agents.

CrewAI is built on three core abstractions, all class-based via decorators:

    - Agent : a worker with a role / goal / backstory (defined in
              config/agents.yaml).
    - Task  : a unit of work with a description / expected_output, assigned
              to an agent (defined in config/tasks.yaml).
    - Crew  : the assembly of agents + tasks that actually runs.

@CrewBase wires the class to the YAML config, exposing self.agents_config
and self.tasks_config. The @agent / @task / @crew decorators register each
method, and self.agents / self.tasks collect everything for the Crew.

Run with .kickoff(inputs=...), where inputs fill the {placeholders} used in
the task descriptions (here, {sentence}).
"""

import dotenv

dotenv.load_dotenv()

from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task

from tools import count_letters


@CrewBase
class TranslatorCrew:
    @agent
    def translator_agent(self):
        return Agent(
            config=self.agents_config["translator_agent"],
        )

    @agent
    def counter_agent(self):
        return Agent(
            config=self.agents_config["counter_agent"],
            tools=[count_letters],
        )

    @task
    def translate_task(self):
        return Task(
            config=self.tasks_config["translate_task"],
        )

    @task
    def retranslate_task(self):
        return Task(
            config=self.tasks_config["retranslate_task"],
        )

    @task
    def count_task(self):
        return Task(
            config=self.tasks_config["count_task"],
        )

    @crew
    def assemble_crew(self):
        return Crew(  # combination of agents and tasks
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,  # console log
        )


if __name__ == "__main__":
    TranslatorCrew().assemble_crew().kickoff(
        inputs={"sentence": "i am hyunsoo and i like to ride bicycle"}
    )
