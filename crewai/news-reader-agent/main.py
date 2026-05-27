import dotenv

dotenv.load_dotenv()

from crewai import Crew, Agent, Task
from crewai.project import CrewBase, agent, task, crew

from tools import search_tool, scrape_tool


@CrewBase
class NewReaderAgent:
    @agent
    def news_hunter_agent(self):
        return Agent(
            config=self.agents_config["news_hunter_agent"],
            tools=[
                search_tool,
                scrape_tool,
            ],
        )

    @agent
    def summarizer_agent(self):
        return Agent(
            config=self.agents_config["summarizer_agent"],
            tools=[
                scrape_tool,
            ],
        )

    @agent
    def curator_agent(self):
        return Agent(
            config=self.agents_config["curator_agent"],
        )

    @task
    def content_harvesting_task(self):
        return Task(
            config=self.tasks_config["content_harvesting_task"]
        )

    # The result of the above task is transmitted to the next task automatically.
    # In other words, you don't need to write parameters ({}) in the prompt in
    # tasks.yaml. But you must state in the prompt that this task needs the result above.
    @task
    def summarization_task(self):
        return Task(
            config=self.tasks_config["summarization_task"]
        )

    # The result here becomes the final_output.
    @task
    def final_report_assembly_task(self):
        return Task(
            config=self.tasks_config["final_report_assembly_task"]
        )

    @crew
    def crew(self):
        return Crew(  # combination of agents and tasks
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,  # console log
        )


if __name__ == "__main__":
    NewReaderAgent().crew().kickoff(inputs={"topic": "cambodia kidnapped"})
