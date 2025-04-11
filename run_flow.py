"""
Alternative script to run the flow directly without UV's hardlinking
which can cause issues in cloud-synced folders like OneDrive.
"""
import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set UV configuration to avoid hardlinks
os.environ["UV_NO_HARDLINKS"] = "1"

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Option 1: Run directly with Python
def run_with_python():
    # Import and run the main function
    from prototype3.main import kickoff
    print("🚀 Running with direct Python execution...")
    kickoff()

# Option 2: Run with modified UV environment (disables hardlinks)
def run_with_uv():
    # Set environment variables to disable hardlinks in UV
    env = os.environ.copy()
    env["UV_NO_HARDLINKS"] = "1"
    
    # Run the flow via UV with modified environment
    print("🚀 Attempting to run with UV (hardlinks disabled)...")
    try:
        subprocess.run(["uv", "run", "safe_kickoff"], env=env, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"⚠️ Could not run with UV: {e}")
        return False

if __name__ == "__main__":
    # If FORCE_DIRECT_PYTHON is set, skip UV attempt
    if os.environ.get("FORCE_DIRECT_PYTHON") == "1":
        run_with_python()
    else:
        # Try UV first, then fall back to direct Python
        if not run_with_uv():
            print("🔄 Falling back to direct Python execution...")
            run_with_python()
