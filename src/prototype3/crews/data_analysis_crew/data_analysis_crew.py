import glob
import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
import json

from dotenv import load_dotenv
from .tools.pandas_query_tool import PandasQueryTool
from langchain_openai import AzureChatOpenAI
import litellm

# Load environment variables from .env file
load_dotenv()

# Configure litellm explicitly for Azure OpenAI
litellm.drop_params = True
litellm.api_type = "azure"
litellm.api_version = "2024-05-01-preview"
litellm.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
litellm.api_key = os.getenv('AZURE_OPENAI_API_KEY')

# Explicitly map your model name to your Azure deployment name with provider prefix
litellm.model_alias_map = {
    "gpt-4o": "azure/gpt-4o_mimi_test"
}















@CrewBase
class DataAnalysisCrew:
    """Data Analysis Crew for handling CSV data with metadata"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    llm = AzureChatOpenAI(
        deployment_name="gpt-4o_mimi_test",
        model_name="gpt-4o",
        openai_api_version="2024-05-01-preview",
        temperature=0.7,
        azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
        api_key=os.getenv('AZURE_OPENAI_API_KEY')
    )


    @agent
    def data_query_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["data_query_agent"],
            verbose=True,
            tools=[PandasQueryTool()],
            llm=self.llm
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
            verbose=True,
            llm=self.llm
        )
