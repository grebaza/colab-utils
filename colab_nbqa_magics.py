# colab_nbqa_magics.py
from IPython.core.magic import register_line_magic
import os
import sys
from pathlib import Path

@register_line_magic
def nbqa(line):
    """Run nbqa with the given tool and current notebook."""
    tool = line.strip()
    try:
        import ipynbname
        notebook_path = ipynbname.path()
    except:
        from google.colab import _message
        import json
        metadata = json.loads(_message.blocking_request('get_ipynb')['ipynb'])
        notebook_name = metadata['metadata']['colab']['name']
        notebook_path = Path(notebook_name)

    os.system(f"nbqa {tool} {notebook_path}")
