import os
from prototype3.utils.path_utils import get_project_root, get_data_file, get_metadata_file

def debug_paths():
    """
    Debug function to print and check paths to important project files.
    
    Returns:
        dict: Dictionary containing path information and existence checks
    """
    cwd = os.getcwd()
    project_root = get_project_root()
    
    # Check standard paths
    metadata_path = get_metadata_file('OBY01PDT01_metadata.json')
    csv_path = get_data_file('OBY01PDT01.csv')
    
    # Check additional knowledge paths
    knowledge_root = os.path.join(project_root, 'knowledge')
    alt_metadata_path = os.path.join(knowledge_root, 'metadata_about_tables', 'OBY01PDT01_metadata.json')
    alt_csv_path = os.path.join(knowledge_root, 'csvs_with_data', 'OBY01PDT01.csv')
    
    # Collect and print path information
    path_info = {
        "current_directory": cwd,
        "project_root": project_root,
        "standard_paths": {
            "metadata_path": metadata_path,
            "metadata_exists": os.path.exists(metadata_path),
            "csv_path": csv_path,
            "csv_exists": os.path.exists(csv_path)
        },
        "alternate_paths": {
            "knowledge_root": knowledge_root,
            "knowledge_root_exists": os.path.exists(knowledge_root),
            "alt_metadata_path": alt_metadata_path,
            "alt_metadata_exists": os.path.exists(alt_metadata_path),
            "alt_csv_path": alt_csv_path,
            "alt_csv_exists": os.path.exists(alt_csv_path)
        }
    }
    
    # Print summary for quick debugging
    print(f"Current working directory: {cwd}")
    print(f"Project root: {project_root}")
    print(f"Standard metadata path exists: {path_info['standard_paths']['metadata_exists']}")
    print(f"Standard CSV path exists: {path_info['standard_paths']['csv_exists']}")
    
    return path_info

if __name__ == "__main__":
    debug_paths()
