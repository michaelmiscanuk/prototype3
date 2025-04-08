import os

def get_project_root() -> str:
    """Returns project root folder."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

def get_data_file(filename: str) -> str:
    """Returns path to a file in the data folder."""
    return os.path.join(get_project_root(), 'data', filename)

def get_metadata_file(filename: str) -> str:
    """Returns path to a file in the metadata folder."""
    return os.path.join(get_project_root(), 'metadata', filename)
