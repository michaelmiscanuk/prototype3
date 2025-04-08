import os

# Ensure the knowledge directories exist
knowledge_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'knowledge'))
metadata_dir = os.path.join(knowledge_root, 'metadata_about_tables')
csv_dir = os.path.join(knowledge_root, 'csvs_with_data')

# Create directories if they don't exist
for directory in [knowledge_root, metadata_dir, csv_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)
