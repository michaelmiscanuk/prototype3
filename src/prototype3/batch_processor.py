import subprocess
from pathlib import Path
import time
import os

def run_single_analysis(prompt):
    print(f"Starting analysis for: {prompt}")
    os.environ["ANALYSIS_PROMPT"] = prompt
    
    process = subprocess.Popen(
        ["safe_crewai.bat", "flow", "kickoff"],
        env={**os.environ},
        shell=True
    )
    return process

def main():
    # Clear previous results
    results_file = Path(__file__).parent / "analysis_results.txt"
    if results_file.exists():
        results_file.unlink()

    prompts = [
        "What is the amount of men in Prague at the end of Q3 2024?",
        "What is the amount of women in Prague at the end of Q3 2024?",
    ]

    processes = []
    for prompt in prompts:
        process = run_single_analysis(prompt)
        processes.append(process)
        # Add small delay between starts to avoid conflicts
        time.sleep(2)

    # Wait for all to complete
    for process in processes:
        process.wait()

    print("All analyses completed. Check analysis_results.txt for results.")

if __name__ == "__main__":
    main()
