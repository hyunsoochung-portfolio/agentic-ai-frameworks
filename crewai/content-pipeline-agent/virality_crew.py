"""ViralityCrew - scores a tweet or LinkedIn post for virality potential.

NOTE: The blog posts referenced `from virality_crew import ViralityCrew` in the
Flow's `main.py` but did not include this file's source. This is a best-effort
reconstruction following the same CrewAI `@CrewBase` pattern used elsewhere in
this repo. It returns a `Score` via `output_pydantic`, so `result.pydantic` in
the Flow yields a `Score(score=..., reason=...)`.
"""

from crewai import Crew, Agent, Task
from crewai.project import CrewBase, agent, task, crew

from models import Score


@CrewBase
class ViralityCrew:
    @agent
    def virality_analyst_agent(self):
        return Agent(
            config=self.agents_config["virality_analyst_agent"],
        )

    @task
    def virality_scoring_task(self):
        return Task(
            config=self.tasks_config["virality_scoring_task"],
            output_pydantic=Score,
        )

    @crew
    def crew(self):
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
        )
