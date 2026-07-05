import os
import shutil
import subprocess
import tempfile

DEFAULT_TIMEOUT_SECONDS = 5
PYTHON_DOCKER_IMAGE = "python:3.12-slim"

def execute_python_code_in_docker(source_code, timeout_seconds=DEFAULT_TIMEOUT_SECONDS):
    """
    Executes the given Python source code in a Docker container.
    """

    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        code_file_path = os.path.join(temp_dir,"main.py")

        with open(code_file_path, "w", encoding="utf-8") as code_file:
            code_file.write(source_code)
        
        docker_command = [
            "docker", 
            "run",
            "--rm",
            "--network", "none",
            "--memory", "128m",
            "--cpus", "0.5",
            "-v", f"{temp_dir}:/sandbox",
            "-w", "/sandbox",
            PYTHON_DOCKER_IMAGE,
            "python", "main.py"
        ]

        completed_process = subprocess.run(
            docker_command,
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
        return{
            "stdout": error.stdout if error.stdout else "",
            "stderr": error.stderr if error.stderr else "Execution timed out.",
            "exit_code": None,
            "timed_out": True
        }
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)