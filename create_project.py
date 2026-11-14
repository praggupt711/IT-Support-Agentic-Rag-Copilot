from pathlib import Path

# Current Working Directory
root = Path(".")

# Folder to store the project files
folders = [
    "app/api",
    "app/core",
    "app/rag",
    "app/services",
    "data",
    "templates",
    "static",
    "uploads",
    "tests"
]

# Files to create in the project

files = [
    "app/main.py",
    "ingest_sample_kb.py",
    "run.py",
    ".env",
]

# Create the folders
for folder in folders:
    folder_path = root / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    print(f"Created folder: {folder_path}")

# Create the files
for file in files:
    file_path = root / file
    file_path.touch(exist_ok=True)
    print(f"Created file: {file_path}")
    
print("Project structure created successfully.")
