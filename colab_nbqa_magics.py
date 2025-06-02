# colab_nbqa_magics.py

import os
import subprocess

from IPython.core.magic import register_line_magic
from google.colab import drive

# Mount Google Drive (if not already mounted)
try:
    drive.mount('/content/drive', force_remount=False)
except Exception as e:
    print(f"Error mounting Google Drive: {e}")

def locate_nb(notebook_name=None, set_singular=True):
    """Locate the notebook path in Google Drive or temporary Colab directory."""
    found_files = []
    paths = ['/content/drive/MyDrive/Colab Notebooks', '/content']  # Search in Drive and temp dir

    # If no notebook name provided, prompt user or use a fallback
    if not notebook_name:
        print("Warning: Notebook name not provided. Please specify the notebook name or ensure it's saved in Google Drive.")
        return None

    try:
        for path in paths:
            if os.path.exists(path):
                for dirpath, _, files in os.walk(path):
                    for file in files:
                        if file == notebook_name:
                            found_files.append(os.path.join(dirpath, file))
        found_files = list(set(found_files))
        
        if len(found_files) == 1:
            nb_dir = os.path.dirname(found_files[0])
            if set_singular:
                print(f'Singular location found, setting directory: {nb_dir}')
                os.chdir(nb_dir)
                return found_files[0]
        elif not found_files:
            print(f'Notebook "{notebook_name}" not found in {paths}.')
            return None
        elif len(found_files) > 1:
            print('Multiple matches found, returning list of possible locations.')
            print(found_files)
            return found_files[0]  # Return first match as fallback
    except Exception as e:
        print(f"Error locating notebook: {e}")
        return None
    return None

def get_notebook_name() -> str:
    """
    Return the current Colab notebook’s filename (without path),
    using the metadata from get_ipynb. If unavailable, returns an empty string.
    """
    try:
        from google.colab import _message
        metadata = _message.blocking_request('get_ipynb')['ipynb']
        return metadata.get('metadata', {}).get('colab', {}).get('name', '')
    except Exception:
        return ""

@register_line_magic
def nbqa(line):
    """
    Run nbqa with the specified tool on the current notebook or a specified notebook.
    Usage: %nbqa <tool_name> [notebook_name]
    Example: %nbqa ruff my_notebook.ipynb
    """
    args = line.strip().split()
    tool = args[0] if args else ""
    notebook = args[1] if len(args) > 1 else locate_nb()
    
    if not tool:
        print("Please specify a tool to run with nbqa.")
        return
    
    print(f"Running nbqa {tool} on notebook: {notebook}")
    
    # Use subprocess to run the command
    try:
        result = subprocess.run(['nbqa', tool, notebook], check=True, text=True, capture_output=True)
        print(result.stdout)  # Print the output of the command
    except subprocess.CalledProcessError as e:
        print(f"Error running nbqa: {e.stderr}")
