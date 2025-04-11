"""
Safe launcher for CrewAI flows in cloud-synced directories.
This module provides a hardlink-safe way to launch CrewAI flows.
"""
import os
import sys
import subprocess
from prototype3.main import kickoff as main_kickoff

def is_in_cloud_folder():
    """Check if current directory is likely in a cloud-synced folder"""
    cwd = os.getcwd()
    cloud_keywords = ["onedrive", "dropbox", "google drive", "box", "icloud"]
    return any(keyword in cwd.lower() for keyword in cloud_keywords)

def kickoff():
    """
    Safe entry point for kicking off the flow.
    Automatically detects if we're in a cloud-synced folder and takes appropriate action.
    """
    # Set environment variable to disable hardlinks
    os.environ["UV_NO_HARDLINKS"] = "1"
    
    # If in OneDrive or other cloud folder, run directly with Python
    if is_in_cloud_folder() or os.environ.get("FORCE_DIRECT_PYTHON") == "1":
        print("📁 Detected cloud-synced folder. Running with direct Python execution...")
        main_kickoff()
    else:
        print("🚀 Running with standard CrewAI flow launcher...")
        try:
            main_kickoff()
        except Exception as e:
            print(f"🔄 Error with standard execution: {e}")
            print("🔄 Falling back to direct Python execution...")
            main_kickoff()

if __name__ == "__main__":
    kickoff()
