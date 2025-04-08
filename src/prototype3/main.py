#!/usr/bin/env python
import os
import json
from pydantic import BaseModel
from crewai.flow import Flow, listen, start
from prototype3.crews.data_analysis_crew.data_analysis_crew import DataAnalysisCrew
from prototype3.tools.path_debug import debug_paths
from prototype3.utils.path_utils import get_metadata_file

class DataAnalysisState(BaseModel):
    prompt: str = ""  # Changed from user_query
    schema: dict = {}
    result: str = ""

class DataAnalysisFlow(Flow[DataAnalysisState]):
    
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
        prompts = [  # Changed from queries            
            "What was the population of woman v Plzni a v Praze at the end of Q3 in 2024 combined as a sum?",
            "What was the population of chicas v Plzni at the end of Q3 in 2024?"
        ]
        self.state.prompt = prompts[0]  # Changed from user_query

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

    @listen(analyze_data)
    def save_result(self):
        print("Saving analysis result")
        with open("analysis_result.txt", "w", encoding='utf-8') as f:
            f.write(self.state.result)

def kickoff():
    flow = DataAnalysisFlow()
    flow.kickoff()

def plot():
    flow = DataAnalysisFlow()
    flow.plot()

if __name__ == "__main__":
    kickoff()
