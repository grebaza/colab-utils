# colab_nbqa_magics.py

import os
import subprocess
from IPython.core.magic import register_line_magic

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
    Run nbqa with the specified tool on the current notebook.
    Usage: %nbqa <tool_name>
    Example: %nbqa ruff
    """
    tool = line.strip()
    notebook = get_notebook_name()
    if not notebook:
        print("Could not determine notebook name; using '*.ipynb'")
        notebook = "*.ipynb"
    
    print(f"Running nbqa {tool} on notebook: {notebook}")
    
    # Use subprocess to run the command
    try:
        result = subprocess.run(['nbqa', tool, notebook], check=True, text=True, capture_output=True)
        print(result.stdout)  # Print the output of the command
    except subprocess.CalledProcessError as e:
        print(f"Error running nbqa: {e.stderr}")
