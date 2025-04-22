import subprocess
from pathlib import Path
import time
import os

def run_single_analysis(prompt):
    print(f"\n[DEBUG] ====== Analysis Start ======")
    print(f"[DEBUG] Processing prompt: {prompt}")
    
    # Get the project root directory (where safe_crewai.bat is)
    root_dir = Path(__file__).parent.parent.parent
    results_file = root_dir / "analysis_results.txt"
    print(f"[DEBUG] Results will be saved to: {results_file}")
    
    # Do NOT clear existing results
    
    print(f"[DEBUG] Setting environment variable ANALYSIS_PROMPT")
    os.environ["ANALYSIS_PROMPT"] = prompt
    
    print("[DEBUG] Executing safe_crewai.bat...")
    
    # Use the full path to safe_crewai.bat
    bat_path = root_dir / "safe_crewai.bat"
    process = subprocess.run(
        [str(bat_path), "flow", "kickoff"],
        env={**os.environ},
        shell=True,
        capture_output=True,
        text=True,
        cwd=str(root_dir)  # Run from project root
    )
    
    print(f"[DEBUG] Process return code: {process.returncode}")
    print(f"[DEBUG] Process stdout length: {len(process.stdout)}")
    print(f"[DEBUG] Process stderr length: {len(process.stderr)}")
    
    if process.stderr:
        print(f"[DEBUG] Process errors: {process.stderr[:200]}...")
    
    # Add delay before reading results
    time.sleep(5)  # Increased delay to ensure file is written
    
    # Try to read the results
    try:
        if not results_file.exists():
            error_msg = f"Results file not found at: {results_file}"
            print(f"[ERROR] {error_msg}")
            return error_msg
            
        with open(results_file, "r", encoding='utf-8') as f:
            content = f.read()
            if not content:
                error_msg = "Results file is empty"
                print(f"[ERROR] {error_msg}")
                return error_msg
                
            print(f"[DEBUG] Successfully read results, length: {len(content)}")
            return content
            
    except Exception as e:
        error_msg = f"Failed to read results: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return error_msg
    
    print("[DEBUG] ====== Analysis Complete ======\n")

def main():
    print("[DEBUG] Starting batch processor main()")
    root_dir = Path(__file__).parent.parent.parent
    results_file = root_dir / "analysis_results.txt"
    
    # Only process a single prompt from environment variable
    prompt = os.environ.get("ANALYSIS_PROMPT")
    if prompt:
        print(f"[DEBUG] Processing prompt from environment: {prompt}")
        output = run_single_analysis(prompt)
        print(f"[DEBUG] Output received, length: {len(output)}")
    else:
        print("[ERROR] No ANALYSIS_PROMPT environment variable found")

if __name__ == "__main__":
    main()
