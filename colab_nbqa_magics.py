# colab_nbqa_magics.py

import os
import shlex
import subprocess
from IPython.core.magic import register_line_magic
from google.colab import drive, output as colab_output

# Mount Google Drive (if not already mounted)
try:
    drive.mount("/content/drive", force_remount=False)
except Exception:
    pass


def locate_file(name: str) -> str:
    """
    Search for a file by exact name in common Colab directories.
    Returns the first matching path or raises FileNotFoundError.
    """
    for base in ("/content/drive/MyDrive/Colab Notebooks", "/content"):
        if not os.path.isdir(base):
            continue
        for dirpath, _, files in os.walk(base):
            if name in files:
                return os.path.join(dirpath, name)
    raise FileNotFoundError(f'File "{name}" not found.')


def current_notebook_name() -> str:
    """
    Get the current Colab notebook’s filename via metadata.
    Returns empty string on failure.
    """
    try:
        from google.colab import _message

        md = _message.blocking_request("get_ipynb")["ipynb"]
        return md.get("metadata", {}).get("colab", {}).get("name", "")
    except Exception:
        return ""


@register_line_magic
def nbqa(line):
    """
    Pass all arguments verbatim to nbqa.
    Usage examples in Colab:
      %nbqa black my_notebook.ipynb
      %nbqa flake8 --ignore=E203 path/to/notebook.ipynb
    """
    line = line.strip()
    if not line:
        print("Usage: %nbqa <nbqa-arguments>")
        return

    # Split the line into arguments and prepend 'nbqa'
    args = shlex.split(line)
    cmd = ["nbqa"] + args

    print("Running:", " ".join(shlex.quote(c) for c in cmd))

    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr)

    # Once nbqa has finished, reload the notebook tab so changes appear
    try:
        colab_output.eval_js("google.colab.notebook.reload()")
    except Exception:
        # If eval_js fails, just remind the user to refresh manually
        print("Could not auto-reload. Please refresh the browser tab to see changes.")
