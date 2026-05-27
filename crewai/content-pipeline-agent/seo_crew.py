"""SeoCrew - scores a blog post for SEO quality.

NOTE: The blog posts referenced `from seo_crew import SeoCrew` in the Flow's
`main.py` but did not include this file's source. This is a best-effort
reconstruction following the same CrewAI `@CrewBase` pattern used in the news
reader and job hunter projects. It returns a `Score` via `output_pydantic`, so
`result.pydantic` in the Flow yields a `Score(score=..., reason=...)`.
"""

from crewai import Crew, Agent, Task
from crewai.project import CrewBase, agent, task, crew

from models import Score


@CrewBase
class SeoCrew:
    @agent
    def seo_analyst_agent(self):
        return Agent(
            config=self.agents_config["seo_analyst_agent"],
        )

    @task
    def seo_scoring_task(self):
        return Task(
            config=self.tasks_config["seo_scoring_task"],
            output_pydantic=Score,
        )

    @crew
    def crew(self):
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
        )
