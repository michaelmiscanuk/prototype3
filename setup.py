"""
Setup script to initialize the project environment
"""
import os
import sys
import shutil
from pathlib import Path

def ensure_directory(directory):
    """Ensure a directory exists"""
    os.makedirs(directory, exist_ok=True)
    print(f"✅ Ensured directory exists: {directory}")

def create_symbolic_link(source, target):
    """Create a symbolic link if possible"""
    try:
        # Remove target if it exists
        if os.path.exists(target):
            if os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.unlink(target)
                
        # Create symbolic link
        os.symlink(source, target, target_is_directory=os.path.isdir(source))
        print(f"✅ Created symbolic link: {source} -> {target}")
    except Exception as e:
        print(f"❌ Could not create symbolic link: {e}")
        print(f"   Falling back to directory copy: {source} -> {target}")
        if os.path.isdir(source):
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)

def setup_project():
    """Set up the project environment"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure required directories exist
    directories = [
        os.path.join(project_root, "data"),
        os.path.join(project_root, "metadata"),
        os.path.join(project_root, "knowledge"),
        os.path.join(project_root, "knowledge", "metadata_about_tables"),
        os.path.join(project_root, "knowledge", "csvs_with_data"),
    ]
    
    for directory in directories:
        ensure_directory(directory)
    
    # Setup data links/copies for compatibility
    data_file = os.path.join(project_root, "data", "OBY01PDT01.csv")
    alt_data_file = os.path.join(project_root, "knowledge", "csvs_with_data", "OBY01PDT01.csv")
    
    metadata_file = os.path.join(project_root, "metadata", "OBY01PDT01_metadata.json")
    alt_metadata_file = os.path.join(project_root, "knowledge", "metadata_about_tables", "OBY01PDT01_metadata.json")
    
    # Create symbolic links or copies if original files exist
    if os.path.exists(data_file) and not os.path.exists(alt_data_file):
        create_symbolic_link(data_file, alt_data_file)
    elif os.path.exists(alt_data_file) and not os.path.exists(data_file):
        create_symbolic_link(alt_data_file, data_file)
        
    if os.path.exists(metadata_file) and not os.path.exists(alt_metadata_file):
        create_symbolic_link(metadata_file, alt_metadata_file)
    elif os.path.exists(alt_metadata_file) and not os.path.exists(metadata_file):
        create_symbolic_link(alt_metadata_file, metadata_file)
    
    print("\n✅ Project setup complete!\n")
    print("To run the project:")
    print("1. Use safe_crewai.bat flow kickoff")
    print("   OR")
    print("2. python run_flow.py")
    
if __name__ == "__main__":
    setup_project()
