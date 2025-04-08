import os

def debug_paths():
    """Debug function to print current paths and check if files exist"""
    cwd = os.getcwd()
    
    # Check paths relative to current working directory
    metadata_path = os.path.join(cwd, "knowledge/metadata_about_tables/OBY01PDT01_metadata.json")
    csv_path = os.path.join(cwd, "knowledge/csvs_with_data/OBY01PDT01.csv")
    
    print(f"Current working directory: {cwd}")
    print(f"Metadata file path: {metadata_path}")
    print(f"Metadata file exists: {os.path.exists(metadata_path)}")
    print(f"CSV file path: {csv_path}")
    print(f"CSV file exists: {os.path.exists(csv_path)}")
    
    return {
        "cwd": cwd,
        "metadata_path": metadata_path,
        "metadata_exists": os.path.exists(metadata_path),
        "csv_path": csv_path,
        "csv_exists": os.path.exists(csv_path)
    }

if __name__ == "__main__":
    debug_paths()
