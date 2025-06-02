# colab_nbqa_magics.py

import os
import subprocess
from IPython.core.magic import register_line_magic
from google.colab import drive, output as colab_output

# Mount Google Drive (if not already mounted)
try:
    drive.mount('/content/drive', force_remount=False)
except Exception:
    pass

def locate_nb(notebook_name: str) -> str:
    """
    Locate the full path of the notebook in Google Drive or /content.
    Returns the first match or raises FileNotFoundError.
    """
    search_paths = [
        '/content/drive/MyDrive/Colab Notebooks',
        '/content'
    ]
    matches = []
    for base in search_paths:
        if os.path.isdir(base):
            for dirpath, _, files in os.walk(base):
                if notebook_name in files:
                    matches.append(os.path.join(dirpath, notebook_name))
    if not matches:
        raise FileNotFoundError(f'Notebook "{notebook_name}" not found in {search_paths}')
    return matches[0]  # return first match

def get_notebook_name() -> str:
    """
    Returns the current Colab notebook’s filename (without path) via metadata.
    """
    try:
        from google.colab import _message
        md = _message.blocking_request('get_ipynb')['ipynb']
        return md.get('metadata', {}).get('colab', {}).get('name', '')
    except Exception:
        return ""

@register_line_magic
def nbqa(line):
    """
    Run nbqa with the specified tool on the current notebook (or given notebook name).
    Usage: %nbqa <tool> [notebook.ipynb]
    """
    parts = line.strip().split()
    if not parts:
        print("Usage: %nbqa <tool> [notebook.ipynb]")
        return
    tool = parts[0]
    if len(parts) > 1:
        nb_name = parts[1]
    else:
        nb_name = get_notebook_name()
        if not nb_name:
            print("Error: Could not determine current notebook name. Provide notebook file explicitly.")
            return

    try:
        nb_path = locate_nb(nb_name)
    except FileNotFoundError as e:
        print(e)
        return

    print(f'Running: nbqa {tool} "{nb_path}"')
    try:
        result = subprocess.run(
            ['nbqa', tool, nb_path],
            check=True,
            text=True,
            capture_output=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
