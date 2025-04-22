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
        
        # Use environment variable if available, otherwise use default
        self.state.prompt = os.getenv("ANALYSIS_PROMPT", "What is the amount of men in Prague at the end of Q3 2024?")

    @tracer.chain
    @listen(process_prompt)
    def analyze_data(self):
        print("[DEBUG] Starting analyze_data method")
        print(f"[DEBUG] Current prompt: {self.state.prompt}") 
        crew = DataAnalysisCrew()
        print("[DEBUG] DataAnalysisCrew instance created")
        try:
            print("[DEBUG] Attempting to kickoff crew")
            # Fix: Pass inputs to the crew's kickoff method
            result = crew.crew().kickoff(inputs={
                "prompt": self.state.prompt,
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
        # Changed to append mode - 'a' instead of 'w'
        with open("analysis_results.txt", "a", encoding='utf-8') as f:
            f.write(f"\nPrompt: {self.state.prompt}\n")
            f.write(f"Result: {self.state.result}\n")
            f.write("-" * 50 + "\n")

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
