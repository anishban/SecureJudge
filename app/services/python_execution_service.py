import subprocess
import tempfile
import os
import sys

DEFAULT_TIMEOUT_SECONDS = 5

def execute_python_code(source_code, timeout_seconds=DEFAULT_TIMEOUT_SECONDS):
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as temp_file:
            temp_file.write(source_code)
            temp_file_path = temp_file.name
        completed_process = subprocess.run(
            [sys.executable, temp_file_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        return {
            "stdout": completed_process.stdout,
            "stderr": completed_process.stderr,
            "exit_code": completed_process.returncode,
            "timed_out": False
        }
    
    except subprocess.TimeoutExpired as error:
        return {
            "stdout": error.stdout or "",
            "stderr": error.stderr or "Execution timed out",
            "exit_code": None,
            "timed_out": True
        }
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)