# colab_nbqa_magics.py

import os
import time
from pathlib import Path
from IPython.core.magic import register_line_magic
from IPython import get_ipython
from google.colab import output as _colab_output

def get_notebook_name(timeout: float = 2.0) -> str:
    """
    Return the current Colab notebook’s filename (without path).
    Uses JavaScript to read document.title, with a metadata fallback.
    """
    notebook_name = {"value": None}

    def _capture(name):
        notebook_name["value"] = name

    _colab_output.register_callback('notebook_name', _capture)

    js = """
    (async () => {
      const name = document.title.split(' - ')[0];
      console.log("nb:" + name);
      google.colab.kernel.invokeFunction('notebook_name', [name], {});
    })();
    """
    _colab_output.eval_js(js)

    t0 = time.time()
    while time.time() - t0 < timeout:
        if notebook_name["value"]:
            return notebook_name["value"]
        time.sleep(0.05)

    # Fallback: try metadata (may be empty if unsaved)
    try:
        md = _colab_output.eval_js("google.colab.kernel.accessRange()")  # triggers get_ipynb
        from google.colab import _message
        metadata = _message.blocking_request('get_ipynb')['ipynb']
        return metadata.get("metadata", {}).get("colab", {}).get("name", "")
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
        print("Could not determine notebook name. Using '*.ipynb'")
        notebook = "*.ipynb"
    print(f"Running nbqa {tool} on notebook: {notebook}")
    return os.system(f'nbqa {tool} "{notebook}"')
