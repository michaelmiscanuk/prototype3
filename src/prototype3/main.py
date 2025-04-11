#!/usr/bin/env python
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from phoenix.otel import register

# Load environment variables
load_dotenv()

# Configure Phoenix tracer using the successful approach
print("Initializing Phoenix tracing...")
tracer_provider = register(
    project_name="CrewAI_Prototype3",  # Project name that will appear in the UI
    auto_instrument=True               # Auto-instrument supported libraries
)
tracer = tracer_provider.get_tracer(__name__)

print("✅ Phoenix tracing initialized")

from crewai.flow import Flow, listen, start
from prototype3.crews.data_analysis_crew.data_analysis_crew import DataAnalysisCrew
from prototype3.tools.path_debug import debug_paths
from prototype3.utils.path_utils import get_metadata_file

class DataAnalysisState(BaseModel):
    prompt: str = ""  # Changed from user_query
    schema: dict = {}
    result: str = ""

class DataAnalysisFlow(Flow[DataAnalysisState]):
    @tracer.chain
    @start()
    def process_prompt(self):  # Changed from process_query
        # Debug paths before starting
        paths_info = debug_paths()
        print(f"Path check results: {paths_info}")
        
        # Load schema
        schema_path = get_metadata_file('OBY01PDT01_metadata.json')
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.state.schema = json.load(f)
        
        # Example prompts that should work:
        prompts = [
            # [0] Answer: 0.944 (676,069 men / 716,056 women)
            "What is the ratio of men to women in Prague at the end of Q3 2024?",

            # [1] Answer: Středočeský kraj (Growth: 6,672 people, from 1,455,940 to 1,462,612)
            "Which region had the highest population growth between start and end of Q3 2024?",

            # [2] Answer: 9,505,112 people (Total 10,897,237 - Prague 1,392,125)
            "What is the total population of all regions except Prague at the end of Q3 2024?",

            # [3] Answer: Moravskoslezský: 603,498 vs Jihomoravský: 625,903 (difference: 22,405 more in Jihomoravský)
            "Compare the number of women in Moravskoslezský kraj and Jihomoravský kraj at the end of Q3 2024",

            # [4] Answer: 12.77% (1,392,125 / 10,897,237 * 100)
            "What percentage of Czech total population lives in Prague at the end of Q3 2024?",

            # [5] Answer: -5,730 people (1,183,474 - 1,189,204)
            "How much did the population of Moravskoslezský kraj change during Q3 2024?",

            # [6] Answer: Karlovarský kraj with 293,218 people
            "Which region has the smallest total population at the end of Q3 2024?",

            # [7] Answer: 51.68% women (625,903 / 1,227,503 * 100)
            "What is the percentage of women in the total population of Jihomoravský kraj at the end of Q3 2024?",

            # [8] Answer: 1.004 (5,549,314 women / 5,347,923 men)
            "What is the ratio of women to men in the total Czech population at the end of Q3 2024?",

            # [9] Answer: Praha (716,056), Středočeský (743,608), Jihomoravský (625,903) = 2,085,567 women
            "What is the combined number of women in Prague, Středočeský and Jihomoravský kraj at the end of Q3 2024?"
        ]
        self.state.prompt = prompts[3]  # Changed from user_query

    @tracer.chain
    @listen(process_prompt)  # Changed from process_query
    def analyze_data(self):
        print("[DEBUG] Starting analyze_data method")
        print(f"[DEBUG] Current prompt: {self.state.prompt}")  # Changed from user_query
        crew = DataAnalysisCrew()
        print("[DEBUG] DataAnalysisCrew instance created")
        try:
            print("[DEBUG] Attempting to kickoff crew")
            # Fix: Pass inputs to the crew's kickoff method
            result = crew.crew().kickoff(inputs={
                "prompt": self.state.prompt,  # Changed from user_query
                "schema": self.state.schema
            })
            print("[DEBUG] Crew kickoff successful")
            print(f"[DEBUG] Result type: {type(result)}")
            self.state.result = result.raw
        except Exception as e:
            print(f"[DEBUG] Error during crew execution: {str(e)}")
            print(f"[DEBUG] Error type: {type(e)}")
            raise

    @tracer.chain
    @listen(analyze_data)
    def save_result(self):
        print("Saving analysis result")
        with open("analysis_result.txt", "w", encoding='utf-8') as f:
            f.write(self.state.result)

def kickoff():
    # Add a trace for the whole flow execution
    with tracer.start_as_current_span("crewai_flow_execution") as span:
        span.set_attribute("flow_name", "DataAnalysisFlow")
        
        flow = DataAnalysisFlow()
        flow.kickoff()

def plot():
    flow = DataAnalysisFlow()
    flow.plot()

def main():
    """Entry point for direct Python execution without UV"""
    kickoff()

if __name__ == "__main__":
    # Use the main function for direct Python execution
    main()
