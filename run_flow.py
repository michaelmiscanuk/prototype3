"""
Alternative script to run the flow directly without UV's hardlinking
which can cause issues in cloud-synced folders like OneDrive.
"""
import os
import sys
import traceback
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set UV configuration to avoid hardlinks
os.environ["UV_NO_HARDLINKS"] = "1"

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def run_with_python():
    """Run directly with Python for maximum compatibility"""
    try:
        # Import and run the main function
        print("🚀 Running with direct Python execution...")
        from prototype3.main import kickoff
        kickoff()
        return True
    except Exception as e:
        print(f"❌ Error in direct Python execution: {e}")
        print("Detailed error:")
        traceback.print_exc()
        return False

def run_with_uv():
    """Run with UV but with hardlinks disabled for compatibility"""
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
    success = False
    
    # If FORCE_DIRECT_PYTHON is set, skip UV attempt
    if os.environ.get("FORCE_DIRECT_PYTHON") == "1":
        success = run_with_python()
    else:
        # Try UV first, then fall back to direct Python
        success = run_with_uv()
        if not success:
            print("🔄 Falling back to direct Python execution...")
            success = run_with_python()
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
