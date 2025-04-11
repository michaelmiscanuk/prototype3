"""
Safe launcher for CrewAI flows in cloud-synced directories.
This module provides a hardlink-safe way to launch CrewAI flows.
"""
import os
import sys
import traceback
from dotenv import load_dotenv
from prototype3.main import kickoff as main_kickoff

# Ensure environment variables are loaded
load_dotenv()

def is_in_cloud_folder():
    """
    Check if current directory is likely in a cloud-synced folder
    
    Returns:
        bool: True if in a cloud-synced folder, False otherwise
    """
    cwd = os.getcwd().lower()
    cloud_keywords = ["onedrive", "dropbox", "google drive", "box", "icloud"]
    return any(keyword in cwd for keyword in cloud_keywords)

def kickoff():
    """
    Safe entry point for kicking off the flow.
    Automatically detects if we're in a cloud-synced folder and takes appropriate action.
    """
    # Set environment variable to disable hardlinks
    os.environ["UV_NO_HARDLINKS"] = "1"
    
    # Log the execution environment
    if is_in_cloud_folder():
        print("📁 Detected cloud-synced folder (OneDrive/Dropbox/etc.)")
        
    if os.environ.get("FORCE_DIRECT_PYTHON") == "1":
        print("⚙️ FORCE_DIRECT_PYTHON is enabled, using direct execution")
        
    # Run with the appropriate method
    try:
        print("🚀 Starting CrewAI flow execution...")
        main_kickoff()
        print("✅ Flow execution completed successfully")
        return True
    except Exception as e:
        print(f"❌ Error during flow execution: {e}")
        print("Detailed error:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = kickoff()
    sys.exit(0 if success else 1)
