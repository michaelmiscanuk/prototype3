import glob
import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
import json
from .tools.pandas_query_tool import PandasQueryTool


@CrewBase
class DataAnalysisCrew:
    """Data Analysis Crew for handling CSV data with metadata"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def data_query_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["data_query_agent"],
            verbose=True,
            tools=[PandasQueryTool()]
        )

    @task
    def process_prompt(self) -> Task:  # Changed from process_query
        return Task(
            config=self.tasks_config["process_prompt"],  # Changed from process_query
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Data Analysis Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
