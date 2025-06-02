# colab_nbqa_magics.py

import os
import shlex
import subprocess
from IPython.core.magic import register_line_magic
from google.colab import drive

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
    %nbqa <tool> [tool_args...] [notebook.ipynb or any file.ext]

    - Detects a filename among the arguments (or uses current notebook name).
    - Passes all other args to nbqa.
    """
    parts = shlex.split(line or "")
    if not parts:
        print("Usage: %nbqa <tool> [tool_args...] [file.ext]")
        return

    tool, *rest = parts

    # Identify file argument (first matching file in search paths)
    file_path = None
    tool_args = []
    for arg in rest:
        try:
            candidate = locate_file(arg)
            file_path = candidate
            continue  # skip adding to tool_args
        except FileNotFoundError:
            tool_args.append(arg)

    # If no file found among args, try current notebook name
    if not file_path:
        name = current_notebook_name()
        if not name:
            print(
                "Error: Cannot determine notebook name; please specify a file explicitly."
            )
            return
        try:
            file_path = locate_file(name)
        except FileNotFoundError as e:
            print(e)
            return

    cmd = ["nbqa", tool] + tool_args + [file_path]
    print("Running:", " ".join(shlex.quote(x) for x in cmd))

    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr)
