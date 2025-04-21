import subprocess
import os
import sys
from pathlib import Path

def run_analysis(prompt):
    # Get the path to main.py
    main_script = Path(__file__).parent / "main.py"
    
    # Create a temporary environment file for this run
    env_file = Path(__file__).parent / f"temp_env_{hash(prompt)}.txt"
    with open(env_file, "w", encoding='utf-8') as f:
        f.write(prompt)
    
    # Run the analysis in a new process
    try:
        print(f"Starting analysis for prompt: {prompt}")
        process = subprocess.Popen(
            [sys.executable, str(main_script)],
            env={**os.environ, "ANALYSIS_PROMPT": prompt}
        )
        return process
    except Exception as e:
        print(f"Error starting process for '{prompt}': {e}")
        return None

def main():
    # Clear previous results
    results_file = Path(__file__).parent / "analysis_results.txt"
    if results_file.exists():
        results_file.unlink()

    prompts = [
        "What is the amount of men in Prague at the end of Q3 2024?",
        "What is the amount of women in Prague at the end of Q3 2024?",
    ]

    # Start all processes
    processes = []
    for prompt in prompts:
        process = run_analysis(prompt)
        if process:
            processes.append(process)

    # Wait for all processes to complete
    for process in processes:
        process.wait()

    print("All analyses completed. Check analysis_results.txt for results.")

if __name__ == "__main__":
    main()
