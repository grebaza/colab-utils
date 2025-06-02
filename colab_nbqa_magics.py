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
    Run nbqa with the specified tool on the current notebook or a specified notebook.
    Usage: %nbqa <tool_name> [notebook_name]
    Example: %nbqa ruff my_notebook.ipynb
    """
    args = line.strip().split()
    tool = args[0] if args else ""
    notebook = args[1] if len(args) > 1 else get_notebook_name()
    
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
