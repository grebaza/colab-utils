# colab_nbqa_magics.py

import os
import subprocess
import requests
import urllib.parse

from IPython.core.magic import register_line_magic
from google.colab import drive
# Mount Google Drive (if not already mounted)
try:
    drive.mount('/content/drive', force_remount=False)
except Exception as e:
    print(f"Error mounting Google Drive: {e}")

def locate_nb(set_singular=True):
    """Locate the current notebook path in Google Drive."""
    found_files = []
    paths = ['/content/drive/MyDrive']  # Default Google Drive path
    nb_address = 'http://172.28.0.2:9000/api/sessions'
    try:
        response = requests.get(nb_address).json()
        name = urllib.parse.unquote(response[0]['name'])
        for path in paths:
            for dirpath, _, files in os.walk(path):
                for file in files:
                    if file == name:
                        found_files.append(os.path.join(dirpath, file))
        found_files = list(set(found_files))
        if len(found_files) == 1:
            nb_dir = os.path.dirname(found_files[0])
            if set_singular:
                print(f'Singular location found, setting directory: {nb_dir}')
                os.chdir(nb_dir)
                return found_files[0]
        elif not found_files:
            print('Notebook file not found.')
            return None
        elif len(found_files) > 1:
            print('Multiple matches found, returning list of possible locations.')
            return found_files
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
